#Lightning Data Module
from . import __file__
import geopandas as gpd
import glob as glob
from deepforest.main import deepforest
from descartes import PolygonPatch
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.collections import PatchCollection
from pytorch_lightning import LightningModule
import os
import pandas as pd
from torch.nn import functional as F
from torch import optim
import torch
from torchvision import transforms
import torchmetrics
import tempfile
import rasterio
from rasterio.plot import show
from src import data
from src import generate
from src import neon_paths
from src import patches
from src import utils
from shapely.geometry import Point, box

class TreeModel(LightningModule):
    """A pytorch lightning data module
    Args:
        model (str): Model to use. See the models/ directory. The name is the filename, each model should take in the same data loader
    """
    def __init__(self, model, classes, label_dict, loss_weight=None, config=None, *args, **kwargs):
        super().__init__()
    
        self.ROOT = os.path.dirname(os.path.dirname(__file__))    
        self.tmpdir = tempfile.gettempdir()
        if config is None:
            self.config = utils.read_config("{}/config.yml".format(self.ROOT))   
        else:
            self.config = config
        
        self.classes = classes
        self.label_to_index = label_dict
        self.index_to_label = {}
        for x in label_dict:
            self.index_to_label[label_dict[x]] = x 
        
        #Create model 
        self.model = model
        
        #Metrics
        micro_recall = torchmetrics.Accuracy(average="micro")
        macro_recall = torchmetrics.Accuracy(average="macro", num_classes=classes)
        top_k_recall = torchmetrics.Accuracy(average="micro",top_k=self.config["top_k"])

        self.metrics = torchmetrics.MetricCollection(
            {"Micro Accuracy":micro_recall,
             "Macro Accuracy":macro_recall,
             "Top {} Accuracy".format(self.config["top_k"]): top_k_recall
             })

        self.save_hyperparameters(ignore=["loss_weight"])
        
        #Weighted loss
        if torch.cuda.is_available():
            self.loss_weight = torch.tensor(loss_weight, device="cuda", dtype=torch.float)
        else:
            self.loss_weight = torch.ones((classes))    
        
    def training_step(self, batch, batch_idx):
        """Train on a loaded dataset
        """
        #allow for empty data if data augmentation is generated
        individual, inputs, y = batch
        images = inputs["HSI"]
        y_hat = self.model.forward(images)
        loss = F.cross_entropy(y_hat, y, weight=self.loss_weight)    

        return loss
    
    def validation_step(self, batch, batch_idx):
        """Train on a loaded dataset
        """
        #allow for empty data if data augmentation is generated
        individual, inputs, y = batch
        images = inputs["HSI"]        
        y_hat = self.model.forward(images)
        loss = F.cross_entropy(y_hat, y, weight=self.loss_weight)        
        
        # Log loss and metrics
        self.log("val_loss", loss, on_epoch=True)
        
        return loss

    def on_validation_epoch_end(self):
        results = self.predict_dataloader(self.trainer.datamodule.val_dataloader())
        
        final_micro = torchmetrics.functional.accuracy(
            preds=torch.tensor(results.pred_label_top1.values),
            target=torch.tensor(results.label.values),
            average="micro")
        
        final_macro = torchmetrics.functional.accuracy(
            preds=torch.tensor(results.pred_label_top1.values),
            target=torch.tensor(results.label.values),
            average="macro",
            num_classes=self.classes)
        
        self.log("Epoch Micro Accuracy", final_micro)
        self.log("Epoch Macro Accuracy", final_macro)
        
        # Log results by species
        taxon_accuracy = torchmetrics.functional.accuracy(
            preds=torch.tensor(results.pred_label_top1.values),
            target=torch.tensor(results.label.values), 
            average="none", 
            num_classes=self.classes
        )
        taxon_precision = torchmetrics.functional.precision(
            preds=torch.tensor(results.pred_label_top1.values),
            target=torch.tensor(results.label.values),
            average="none",
            num_classes=self.classes
        )
        species_table = pd.DataFrame(
            {"taxonID":self.label_to_index.keys(),
             "accuracy":taxon_accuracy,
             "precision":taxon_precision
             })
        
        for key, value in species_table.set_index("taxonID").accuracy.to_dict().items():
            self.log("Epoch_{}_accuracy".format(key), value)
            
    def configure_optimizers(self):
        optimizer = optim.Adam(self.model.parameters(), lr=self.config["lr"])
        
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer,
                                                         mode='min',
                                                         factor=0.75,
                                                         patience=8,
                                                         verbose=True,
                                                         threshold=0.0001,
                                                         threshold_mode='rel',
                                                         cooldown=0,
                                                         min_lr=0.0000001,
                                                         eps=1e-08)
                                                                 
        return {'optimizer':optimizer, 'lr_scheduler': scheduler,"monitor":'val_loss'}
    

    def predict(self,inputs):
        """Given a input dictionary, construct args for prediction"""
        if "cuda" == self.device.type:
            images = inputs["HSI"]
            images = [x.cuda() for x in images]
            pred = self.model(images)
            pred = pred.cpu()
        else:
            images = inputs["HSI"]
            pred = self.model(images)
        
        return pred
    
    def predict_dataloader(self, data_loader, test_crowns=None, test_points=None, plot_n_individuals=1, return_features=False, experiment=None, train=True):
        """Given a file with paths to image crops, create crown predictions 
        The format of image_path inform the crown membership, the files should be named crownid_counter.png where crownid is a
        unique identifier for each crown and counter is 0..n pixel crops that belong to that crown.
        
        Args: 
            csv_file: path to csv file
            data_loader: data.TreeData loader
            plot_n_individuals: if experiment, how many plots to create
            return_features (False): If true, return a samples x classes matrix of softmax features
        Returns:
            results: if return_features == False, pandas dataframe with columns crown and species label
            features: if return_features == True, samples x classes matrix of softmax features
        """
        self.model.eval()
        predictions = []
        labels = []
        individuals = []
        for batch in data_loader:
            if train:
                individual, inputs, targets = batch
            else:
                individual, inputs = batch
            with torch.no_grad():
                pred = self.predict(inputs)
                pred = F.softmax(pred, dim=1)
            predictions.append(pred)
            individuals.append(individual)
            if train:
                labels.append(targets)                

        individuals = np.concatenate(individuals)        
        predictions = np.concatenate(predictions) 
        
        if train:
            labels = np.concatenate(labels)
        
        predictions_top1 = np.argmax(predictions, 1)    
        predictions_top2 = pd.DataFrame(predictions).apply(lambda x: np.argsort(x.values)[-2], axis=1)
        top1_score = pd.DataFrame(predictions).apply(lambda x: x.sort_values(ascending=False).values[0], axis=1)
        top2_score = pd.DataFrame(predictions).apply(lambda x: x.sort_values(ascending=False).values[1], axis=1)
        
        #Construct a df of predictions
        df = pd.DataFrame({
            "pred_label_top1":predictions_top1,
            "pred_label_top2":predictions_top2,
            "top1_score":top1_score,
            "top2_score":top2_score,
            "individual":individuals
        })
        
        df["pred_taxa_top1"] = df["pred_label_top1"].apply(lambda x: self.index_to_label[x]) 
        df["pred_taxa_top2"] = df["pred_label_top2"].apply(lambda x: self.index_to_label[x])        
        
        if train:
            df["label"] = labels
            df["true_taxa"] = df["label"].apply(lambda x: self.index_to_label[x])            
            
        if experiment:
            #load image pool and crown predicrions
            rgb_pool = glob.glob(self.config["rgb_sensor_pool"], recursive=True)            
            plt.ion()
            for index, row in df.sample(n=plot_n_individuals).iterrows():
                fig = plt.figure(0)
                ax = fig.add_subplot(1, 1, 1)                
                individual = row["individual"]
                try:
                    geom = test_crowns[test_crowns.individual == individual].geometry.iloc[0]
                except Exception as e:
                    print("Cannot find individual {} in crowns.shp with schema {}".format(individual, test_crowns.head()))
                    break
                    
                left, bottom, right, top = geom.bounds
                
                #Find image
                img_path = neon_paths.find_sensor_path(lookup_pool=rgb_pool, bounds=geom.bounds)
                src = rasterio.open(img_path)
                img = src.read(window=rasterio.windows.from_bounds(left-10, bottom-10, right+10, top+10, transform=src.transform))  
                img_transform = src.window_transform(window=rasterio.windows.from_bounds(left-10, bottom-10, right+10, top+10, transform=src.transform))  
                
                #Plot crown
                patches = [PolygonPatch(geom, edgecolor='red', facecolor='none')]
                show(img, ax=ax, transform=img_transform)                
                ax.add_collection(PatchCollection(patches, match_original=True))
                
                #Plot field coordinate
                stem = test_points[test_points.individualID == individual]
                stem.plot(ax=ax)
                
                plt.savefig("{}/{}.png".format(self.tmpdir, row["individual"]))
                experiment.log_image("{}/{}.png".format(self.tmpdir, row["individual"]), name = "crown: {}, True: {}, Predicted {}".format(row["individual"], row.true_taxa,row.pred_taxa_top1))
                src.close()
                plt.close("all")
            plt.ioff()
    
        if return_features:            
            return df, predictions        
        else:
            return df
    
    def evaluate_crowns(self, data_loader, crowns, points=None, experiment=None):
        """Crown level measure of accuracy
        Args:
            data_loader: TreeData dataset
            experiment: optional comet experiment
            points: the canopy_points.shp from the data_module
        Returns:
            df: results dataframe
            metric_dict: metric -> value
        """
        results, features = self.predict_dataloader(
            data_loader=data_loader,
            plot_n_individuals=self.config["plot_n_individuals"],
            experiment=None,
            test_crowns=crowns,
            test_points=points,
            return_features=True
        )
        
        # Read in crowns data
        results = results.merge(crowns.drop(columns="label"), on="individual")
        results = gpd.GeoDataFrame(results, geometry="geometry")    
        
        # Log results by species
        taxon_accuracy = torchmetrics.functional.accuracy(
            preds=torch.tensor(results.pred_label_top1.values),
            target=torch.tensor(results.label.values), 
            average="none", 
            num_classes=self.classes
        )
        taxon_precision = torchmetrics.functional.precision(
            preds=torch.tensor(results.pred_label_top1.values),
            target=torch.tensor(results.label.values),
            average="none",
            num_classes=self.classes
        )
        species_table = pd.DataFrame(
            {"taxonID":self.label_to_index.keys(),
             "accuracy":taxon_accuracy,
             "precision":taxon_precision
             })
        
        if experiment:
            experiment.log_metrics(species_table.set_index("taxonID").accuracy.to_dict(),prefix="accuracy")
            experiment.log_metrics(species_table.set_index("taxonID").precision.to_dict(),prefix="precision")
                
        #Log result by site
        if experiment:
            site_data_frame =[]
            for name, group in results.groupby("siteID"):                
                site_micro = torchmetrics.functional.accuracy(
                    preds=torch.tensor(group.pred_label_top1.values),
                    target=torch.tensor(group.label.values),
                    average="micro")
                
                site_macro = torchmetrics.functional.accuracy(
                    preds=torch.tensor(group.pred_label_top1.values),
                    target=torch.tensor(group.label.values),
                    average="macro",
                    num_classes=self.classes)
                
                experiment.log_metric("{}_macro".format(name), site_macro)
                experiment.log_metric("{}_micro".format(name), site_micro) 
                row = pd.DataFrame({"Site":[name], "Micro Recall": [site_micro.numpy()], "Macro Recall": [site_macro.numpy()]})
                site_data_frame.append(row)
            site_data_frame = pd.concat(site_data_frame)
            experiment.log_table("site_results.csv", site_data_frame)
        
        return results
            
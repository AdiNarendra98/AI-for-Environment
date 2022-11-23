#Ligthning data module
from . import __file__
from distributed import wait
import glob
import geopandas as gpd
import numpy as np
import os
import pandas as pd
from pytorch_lightning import LightningDataModule
from src import generate
from src import CHM
from src import augmentation
from src import megaplot
from src import neon_paths
from src.models import dead
from src.utils import *
from shapely.geometry import Point
import torch
from torch.utils.data import Dataset
import rasterio

def filter_data(path, config):
    """Transform raw NEON data into clean shapefile   
    Args:
        config: DeepTreeAttention config dict, see config.yml
    """
    field = pd.read_csv(path)
    field["individual"] = field["individualID"]
    field = field[~field.itcEasting.isnull()]
    field = field[~field.growthForm.isin(["liana","small shrub"])]
    field = field[~field.growthForm.isnull()]
    field = field[~field.plantStatus.isnull()]        
    field = field[field.plantStatus.str.contains("Live")]    
    
    groups = field.groupby("individual")
    shaded_ids = []
    for name, group in groups:
        shaded = any([x in ["Full shade", "Mostly shaded"] for x in group.canopyPosition.values])
        if shaded:
            if any([x in ["Open grown", "Full sun"] for x in group.canopyPosition.values]):
                continue
            else:
                shaded_ids.append(group.individual.unique()[0])
        
    field = field[~(field.individual.isin(shaded_ids))]
    field = field[(field.height > 3) | (field.height.isnull())]
    field = field[field.stemDiameter > config["min_stem_diameter"]]
    
    #Subspecies filter
    field.loc[field.taxonID=="PSMEM","taxonID"] = "PSME"
    field.loc[field.taxonID=="BEPAP","taxonID"] = "BEPA"
    field.loc[field.taxonID=="ACNEN","taxonID"] = "ACNE2"
    field.loc[field.taxonID=="ACRUR","taxonID"] = "ACRU"
    field.loc[field.taxonID=="PICOL","taxonID"] = "PICO"
    field.loc[field.taxonID=="ABLAL","taxonID"] = "ABLA"
    field.loc[field.taxonID=="ACSA3","taxonID"] = "ACSAS"
    field.loc[field.taxonID=="CECAC","taxonID"] = "CECA4"
    field.loc[field.taxonID=="PRSES","taxonID"] = "PRSE2"
    field.loc[field.taxonID=="PIPOS","taxonID"] = "PIPO"
    field.loc[field.taxonID=="BEPAC2","taxonID"] = "BEPA"
    field.loc[field.taxonID=="JUVIV","taxonID"] = "JUVI"
    field.loc[field.taxonID=="PRPEP","taxonID"] = "PRPE2"
    field.loc[field.taxonID=="COCOC","taxonID"] = "COCO6"    
    field.loc[field.taxonID=="NYBI","taxonID"] = "NYSY"
    
    field = field[~field.taxonID.isin(["BETUL", "FRAXI", "HALES", "PICEA", "PINUS", "QUERC", "ULMUS", "2PLANT"])]
    field = field[~(field.eventID.str.contains("2014"))]
    with_heights = field[~field.height.isnull()]
    with_heights = with_heights.loc[with_heights.groupby('individual')['height'].idxmax()]
    
    missing_heights = field[field.height.isnull()]
    missing_heights = missing_heights[~missing_heights.individual.isin(with_heights.individual)]
    missing_heights = missing_heights.groupby("individual").apply(lambda x: x.sort_values(["eventID"],ascending=False).head(1)).reset_index(drop=True)
  
    field = pd.concat([with_heights,missing_heights])
    
    # Remove multibole
    field = field[~(field.individual.str.contains('[A-Z]$',regex=True))]

    # List of hand cleaned errors
    known_errors = ["NEON.PLA.D03.OSBS.03422","NEON.PLA.D03.OSBS.03422","NEON.PLA.D03.OSBS.03382", "NEON.PLA.D17.TEAK.01883"]
    field = field[~(field.individual.isin(known_errors))]
    field = field[~(field.plotID == "SOAP_054")]
    
    #Create shapefile
    field["geometry"] = [Point(x,y) for x,y in zip(field["itcEasting"], field["itcNorthing"])]
    shp = gpd.GeoDataFrame(field)
    
    # BLAN has some data in 18N UTM, reproject to 17N update columns
    BLAN_errors = shp[(shp.siteID == "BLAN") & (shp.utmZone == "18N")]
    BLAN_errors.set_crs(epsg=32618, inplace=True)
    BLAN_errors.to_crs(32617,inplace=True)
    BLAN_errors["utmZone"] = "17N"
    BLAN_errors["itcEasting"] = BLAN_errors.geometry.apply(lambda x: x.coords[0][0])
    BLAN_errors["itcNorthing"] = BLAN_errors.geometry.apply(lambda x: x.coords[0][1])
    
    # reupdate
    shp.loc[BLAN_errors.index] = BLAN_errors
    
    # Oak Right Lab has no AOP data
    shp = shp[~(shp.siteID.isin(["PUUM","ORNL"]))]

    # There are a couple NEON plots within the OSBS megaplot, make sure they are removed
    shp = shp[~shp.plotID.isin(["OSBS_026","OSBS_029","OSBS_039","OSBS_027","OSBS_036"])]

    return shp

def sample_plots(shp, min_train_samples=5, min_test_samples=3, iteration = 1):
    """Sample and split a pandas dataframe based on plotID
    Args:
        shp: pandas dataframe of filtered tree locations
        test_fraction: proportion of plots in test datasets
        min_samples: minimum number of samples per class
        iteration: a dummy parameter to make dask submission unique
    """
    #When splitting train/test, only use 1 sample per year for counts.
    single_year = shp.groupby("individual").apply(lambda x: x.head(1))
    
    plotIDs = list(shp.plotID.unique())
    if len(plotIDs) <=2:
        test = shp[shp.plotID == shp.plotID.unique()[0]]
        train = shp[shp.plotID == shp.plotID.unique()[1]]

        return train, test
    else:
        plotIDs = shp[shp.siteID=="OSBS"].plotID.unique()

    np.random.shuffle(plotIDs)
    species_to_sample = shp.taxonID.unique()
    
    # Mimic natural sampling
    species_floor = single_year.taxonID.value_counts() * 0.05
    species_floor[species_floor < min_test_samples] = min_test_samples
    species_floor = species_floor.to_dict()
    
    test_plots = []
    for plotID in plotIDs:
        selected_plot = single_year[single_year.plotID == plotID]
        # If any species is missing from min samples, include plot
        if any([x in species_to_sample for x in selected_plot.taxonID.unique()]):
            test_plots.append(plotID)            
            counts = single_year[single_year.plotID.isin(test_plots)].taxonID.value_counts().to_dict()
            species_completed = [key for key, value in counts.items() if value > species_floor[key]]
            species_to_sample = [x for x in shp.taxonID.unique() if not x in species_completed]
    
    #Sample from original multi_year data
    test = shp[shp.plotID.isin(test_plots)]
    train = shp[~shp.plotID.isin(test.plotID.unique())]

    ## Remove fixed boxes from test
    test = test.loc[~test["box_id"].astype(str).str.contains("fixed").fillna(False)]    
    
    testids = test.groupby("individual").apply(lambda x: x.head(1)).groupby("taxonID").filter(lambda x: x.shape[0] >= min_test_samples).individual
    test = test[test.individual.isin(testids)]

    trainids = train.groupby("individual").apply(lambda x: x.head(1)).groupby("taxonID").filter(lambda x: x.shape[0] >= min_train_samples).individual
    train = train[train.individual.isin(trainids)]
    
    train = train[train.taxonID.isin(test.taxonID)]    
    test = test[test.taxonID.isin(train.taxonID)]
    
    return train, test


def train_test_split(shp, config, client = None):
    """Create the train test split
    Args:
        shp: a filter pandas dataframe (or geodataframe)  
        client: optional dask client
    Returns:
        None: train.shp and test.shp are written as side effect
        """    
    min_sampled = config["min_train_samples"] + config["min_test_samples"]
    keep = shp.taxonID.value_counts() > (min_sampled)
    species_to_keep = keep[keep].index
    shp = shp[shp.taxonID.isin(species_to_keep)]
    print("splitting data into train test. Initial data has {} points from {} species with a min of {} samples".format(shp.shape[0],shp.taxonID.nunique(),min_sampled))
    test_species = 0
    ties = []
    if client:
        futures = [ ]
        for x in np.arange(config["iterations"]):
            future = client.submit(
                sample_plots,
                shp=shp,
                min_train_samples=config["min_train_samples"],
                iteration=x,
                min_test_samples=config["min_test_samples"],
            )
            futures.append(future)

        wait(futures)
        for x in futures:
            train, test = x.result()
            if test.taxonID.nunique() > test_species:
                print("Selected test has {} points and {} species".format(test.shape[0], test.taxonID.nunique()))
                saved_train = train
                saved_test = test
                test_species = test.taxonID.nunique()
                ties = []
                ties.append([train, test])
            elif test.taxonID.nunique() == test_species:
                ties.append([train, test])          
    else:
        for x in np.arange(config["iterations"]):
            train, test = sample_plots(
                shp=shp,
                min_train_samples=config["min_train_samples"],
                min_test_samples=config["min_test_samples"],
            )
            if test.taxonID.nunique() > test_species:
                print("Selected test has {} points and {} species".format(test.shape[0], test.taxonID.nunique()))
                saved_train = train
                saved_test = test
                test_species = test.taxonID.nunique()
                #reset ties
                ties = []
                ties.append([train, test])
            elif test.taxonID.nunique() == test_species:
                ties.append([train, test])
    
    # The size of the datasets
    if len(ties) > 1:
        print("The size of tied train datasets with {} species is {}".format(test_species, [x[0].shape[0] for x in ties]))  
        print("The size of tied test datasets with {} species is {}".format(test_species, [x[1].shape[0] for x in ties]))        
        
        saved_train, saved_test = ties[np.argmax([x[0].shape[0] for x in ties])]
        
    train = saved_train
    test = saved_test    
    
    # Give tests a unique index to match against
    test["point_id"] = test.index.values
    train["point_id"] = train.index.values
    
    return train, test

# Dataset class
class TreeDataset(Dataset):
    """A csv file with a path to image crop and label
    Args:
       csv_file: path to csv file with image_path and label
    """
    def __init__(self, df=None, csv_file=None, config=None, train=True):
        if csv_file:
            self.annotations = pd.read_csv(csv_file)
        else:
            self.annotations = df
        
        self.train = train
        self.config = config         
        self.image_size = config["image_size"]
        self.years = self.annotations.tile_year.unique()
        self.individuals = self.annotations.individual.unique()
        self.image_paths = self.annotations.groupby("individual").apply(lambda x: x.set_index('tile_year').image_path.to_dict())
        if train:
            self.labels = self.annotations.set_index("individual").label.to_dict()
        
        # Create augmentor
        self.transformer = augmentation.train_augmentation(image_size=self.image_size)
        self.image_dict = {}
        
        # Pin data to memory if desired
        if self.config["preload_images"]:
            for individual in self.individuals:
                images = []
                ind_annotations = self.image_paths[individual]
                for year in self.years:
                    try:
                        year_annotations = ind_annotations[year]
                        image_path = os.path.join(self.config["crop_dir"], year_annotations)
                        image = load_image(image_path, image_size=self.image_size)                        
                    except KeyError:
                        image = torch.zeros(self.config["bands"], self.config["image_size"], self.config["image_size"])                                            
                    if self.train:
                        image = self.transformer(image)   
                    images.append(image)
                self.image_dict[individual] = images
            
    def __len__(self):
        # 0th based index
        return len(self.individuals)

    def __getitem__(self, index):
        inputs = {}
        individual = self.individuals[index]        
        if self.config["preload_images"]:
            inputs["HSI"] = self.image_dict[individual]
        else:
            images = []
            ind_annotations = self.image_paths[individual]
            for year in self.years:
                try:
                    year_annotations = ind_annotations[year]
                    image_path = os.path.join(self.config["crop_dir"], year_annotations)
                    image = load_image(image_path, image_size=self.image_size)                        
                except Exception:
                    image = torch.zeros(self.config["bands"], self.config["image_size"], self.config["image_size"])                                            
                if self.train:
                    image = self.transformer(image)   
                images.append(image)
            inputs["HSI"] = images
        
        if self.train:
            label = self.labels[individual]
            label = torch.tensor(label, dtype=torch.long)

            return individual, inputs, label
        else:
            return individual, inputs
    
class TreeData(LightningDataModule):
    """
    Lightning data module to convert raw NEON data into HSI pixel crops based on the config.yml file. 
    The module checkpoints the different phases of setup, if one stage failed it will restart from that stage. 
    Use regenerate=True to override this behavior in setup()
    """
    def __init__(self, csv_file, config, HSI=True, metadata=False, client = None, data_dir=None, comet_logger=None, debug=False):
        """
        Args:
            config: optional config file to override
            data_dir: override data location, defaults to ROOT   
            regenerate: Whether to recreate raw data
            debug: a test mode for small samples
        """
        super().__init__()
        self.ROOT = os.path.dirname(os.path.dirname(__file__))
        self.csv_file = csv_file
        self.comet_logger = comet_logger
        self.debug = debug 

        # Default training location
        self.client = client
        self.data_dir = data_dir
        self.config = config

        #add boxes folder if needed
        try:
            os.mkdir(os.path.join(self.data_dir,"boxes"))
        except:
            pass
        
        # Clean data from raw csv, regenerate from scratch or check for progress and complete
        if self.config["use_data_commit"] is None:
            if self.config["replace"]: 
                # Convert raw neon data to x,y tree locatins
                df = filter_data(self.csv_file, config=self.config)
                    
                # Load any megaplot data
                if not self.config["megaplot_dir"] is None:
                    megaplot_data = megaplot.load(directory=self.config["megaplot_dir"], config=self.config, site="OSBS")
                    #Simplify MAGNOLIA's just at OSBS
                    megaplot_data.loc[megaplot_data.taxonID=="MAGR4","taxonID"] = "MAGNO"  
                    #Hold IFAS records seperarely to model on polygons
                    IFAS = megaplot_data[megaplot_data.filename.str.contains("IFAS")]
                    IFAS.geometry = IFAS.geometry.envelope
                    IFAS["box_id"] = list(range(IFAS.shape[0]))
                    IFAS = IFAS[["geometry","taxonID","individual","plotID","siteID","box_id"]]
                    IFAS["individual"] = IFAS["individual"]
                    megaplot_data = megaplot_data[~(megaplot_data.filename.str.contains("IFAS"))]
                    
                    df = pd.concat([megaplot_data, df])
                
                if not self.debug:
                    data_from_other_sites = df[~(df.siteID=="OSBS")]
                    data_from_OSBS = df[(df.siteID=="OSBS")]
                    species_to_keep = df[df.siteID=="OSBS"].taxonID.unique()
                    data_from_other_sites = data_from_other_sites[data_from_other_sites.taxonID.isin(species_to_keep)].groupby("taxonID").apply(lambda x: x.head(self.config["samples_from_other_sites"]))
                    df = pd.concat([data_from_OSBS, data_from_other_sites])
                                    
                if self.comet_logger:
                    self.comet_logger.experiment.log_parameter("Species before CHM filter", len(df.taxonID.unique()))
                    self.comet_logger.experiment.log_parameter("Samples before CHM filter", df.shape[0])
                    
                #Filter points based on LiDAR height
                df = CHM.filter_CHM(df, CHM_pool=self.config["CHM_pool"],
                                    min_CHM_height=self.config["min_CHM_height"], 
                                    max_CHM_diff=self.config["max_CHM_diff"], 
                                    CHM_height_limit=self.config["CHM_height_limit"])  
                
                self.canopy_points = df
                self.canopy_points.to_file("{}/canopy_points.shp".format(self.data_dir))
    
                if self.comet_logger:
                    self.comet_logger.experiment.log_parameter("Species after CHM filter", len(df.taxonID.unique()))
                    self.comet_logger.experiment.log_parameter("Samples after CHM filter", df.shape[0])
            
                # Create crown data
                self.crowns = generate.points_to_crowns(
                    field_data="{}/canopy_points.shp".format(self.data_dir),
                    rgb_dir=self.config["rgb_sensor_pool"],
                    savedir="{}/boxes/".format(self.data_dir),
                    raw_box_savedir="{}/boxes/".format(self.data_dir), 
                    client=self.client
                )
                
                if self.config["megaplot_dir"]:
                    #ADD IFAS back in, use polygons instead of deepforest boxes                    
                    self.crowns = gpd.GeoDataFrame(pd.concat([self.crowns, IFAS]))
                
                if self.comet_logger:
                    self.crowns.to_file("{}/crowns.shp".format(self.data_dir))
                    self.comet_logger.experiment.log_parameter("Species after crown prediction", len(self.crowns.taxonID.unique()))
                    self.comet_logger.experiment.log_parameter("Samples after crown prediction", self.crowns.shape[0])
                
                if self.comet_logger:
                    self.comet_logger.experiment.log_parameter("Species after dead filtering",len(self.crowns.taxonID.unique()))
                    self.comet_logger.experiment.log_parameter("Samples after dead filtering",self.crowns.shape[0])
                    try:
                        rgb_pool = glob.glob(self.config["rgb_sensor_pool"], recursive=True)
                        for index, row in self.predicted_dead.iterrows():
                            left, bottom, right, top = row["geometry"].bounds                
                            img_path = neon_paths.find_sensor_path(lookup_pool=rgb_pool, bounds=row["geometry"].bounds)
                            src = rasterio.open(img_path)
                            img = src.read(window=rasterio.windows.from_bounds(left-4, bottom-4, right+4, top+4, transform=src.transform))                      
                            img = np.rollaxis(img, 0, 3)
                            self.comet_logger.experiment.log_image(image_data=img, name="Dead: {} ({:.2f}) {}".format(row["dead_label"],row["dead_score"],row["individual"]))                        
                    except:
                        print("No dead trees predicted")
            else:
                self.crowns = gpd.read_file("{}/crowns.shp".format(self.data_dir))
    
            annotations = generate.generate_crops(
                self.crowns,
                savedir=self.config["crop_dir"],
                sensor_glob=self.config["HSI_sensor_pool"],
                convert_h5=self.config["convert_h5"],   
                rgb_glob=self.config["rgb_sensor_pool"],
                HSI_tif_dir=self.config["HSI_tif_dir"],
                client=self.client,
                replace=self.config["replace"]
            )
            
            annotations.to_csv("{}/annotations.csv".format(self.data_dir))
            
            if self.comet_logger:
                self.comet_logger.experiment.log_parameter("Species after crop generation",len(annotations.taxonID.unique()))
                self.comet_logger.experiment.log_parameter("Samples after crop generation",annotations.shape[0])
                
            if self.config["new_train_test_split"]:
                self.train, self.test = train_test_split(annotations, config=self.config, client=self.client) 
                
                self.train.to_csv("{}/train.csv".format(self.data_dir))
                self.test.to_csv("{}/test.csv".format(self.data_dir))
                
            else:
                previous_train = pd.read_csv("{}/train.csv".format(self.data_dir))
                previous_test = pd.read_csv("{}/test.csv".format(self.data_dir))
                
                self.train = annotations[annotations.individual.isin(previous_train.individual)]
                self.test = annotations[annotations.individual.isin(previous_test.individual)]
                
            # Capture discarded species
            individuals = np.concatenate([self.train.individual.unique(), self.test.individual.unique()])
            self.novel = annotations[~annotations.individual.isin(individuals)]
            self.novel = self.novel[~self.novel.taxonID.isin(np.concatenate([self.train.taxonID.unique(), self.test.taxonID.unique()]))]
            self.novel.to_csv("{}/novel_species.csv".format(self.data_dir))
            
            # Store class labels
            unique_species_labels = np.concatenate([self.train.taxonID.unique(), self.test.taxonID.unique()])
            unique_species_labels = np.unique(unique_species_labels)
            unique_species_labels = np.sort(unique_species_labels)            
            self.num_classes = len(unique_species_labels)
    
            # Taxon to ID dict and the reverse    
            self.species_label_dict = {}
            for index, taxonID in enumerate(unique_species_labels):
                self.species_label_dict[taxonID] = index
    
            # Store site labels
            unique_site_labels = np.concatenate([self.train.siteID.unique(), self.test.siteID.unique()])
            unique_site_labels = np.unique(unique_site_labels)
            
            self.site_label_dict = {}
            for index, label in enumerate(unique_site_labels):
                self.site_label_dict[label] = index
            self.num_sites = len(self.site_label_dict)                   
            
            self.label_to_taxonID = {v: k  for k, v in self.species_label_dict.items()}
            
            #Encode the numeric site and class data
            self.train["label"] = self.train.taxonID.apply(lambda x: self.species_label_dict[x])
            self.train["site"] = self.train.siteID.apply(lambda x: self.site_label_dict[x])
            
            self.test["label"] = self.test.taxonID.apply(lambda x: self.species_label_dict[x])
            self.test["site"] = self.test.siteID.apply(lambda x: self.site_label_dict[x])
            
            self.train.to_csv("{}/train.csv".format(self.data_dir), index=False)            
            self.test.to_csv("{}/test.csv".format(self.data_dir), index=False)
            
            print("There are {} records for {} species for {} sites in filtered train".format(
                self.train.shape[0],
                len(self.train.label.unique()),
                len(self.train.site.unique())
            ))
            
            print("There are {} records for {} species for {} sites in test".format(
                self.test.shape[0],
                len(self.test.label.unique()),
                len(self.test.site.unique()))
            )
             
        else:
            print("Loading previous run")            
            self.train = pd.read_csv("{}/train.csv".format(self.data_dir))
            self.test = pd.read_csv("{}/test.csv".format(self.data_dir))
            
            try:
                self.train["individual"] = self.train["individualID"]
                self.test["individual"] = self.test["individualID"]
            except:
                pass
            
            self.crowns = gpd.read_file("{}/crowns.shp".format(self.data_dir))
            
            #mimic schema due to abbreviation when .shp is saved
            self.canopy_points = gpd.read_file("{}/canopy_points.shp".format(self.data_dir))
            
            #Store class labels
            unique_species_labels = np.concatenate([self.train.taxonID.unique(), self.test.taxonID.unique()])
            unique_species_labels = np.unique(unique_species_labels)
            unique_species_labels = np.sort(unique_species_labels)            
            self.num_classes = len(unique_species_labels)
            
            #Taxon to ID dict and the reverse    
            self.species_label_dict = {}
            for index, taxonID in enumerate(unique_species_labels):
                self.species_label_dict[taxonID] = index
                
            #Store site labels
            unique_site_labels = np.concatenate([self.train.siteID.unique(), self.test.siteID.unique()])
            unique_site_labels = np.unique(unique_site_labels)
            
            self.site_label_dict = {}
            for index, label in enumerate(unique_site_labels):
                self.site_label_dict[label] = index
            self.num_sites = len(self.site_label_dict)                   
            
            self.label_to_taxonID = {v: k  for k, v in self.species_label_dict.items()}
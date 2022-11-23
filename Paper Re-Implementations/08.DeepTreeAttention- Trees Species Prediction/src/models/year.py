#Year model
from torch.nn import Module
from torch.nn import functional as F
from torch import nn
import torch
import torchmetrics
from src.models import Hang2020

class learned_ensemble(Module):
    def __init__(self, years, classes, config):
        super().__init__()
        
        self.year_models = nn.ModuleList()
        self.years = years
        for year in range(years):
            #Load from state dict of previous run
            if config["pretrain_state_dict"]:
                base_model = Hang2020.load_from_backbone(state_dict=config["pretrain_state_dict"], classes=classes, bands=config["bands"])
            else:
                base_model = Hang2020.spectral_network(bands=config["bands"], classes=classes)
            
            self.year_models.append(base_model)
        
    def forward(self, images):
        year_scores = []
        for index, x in enumerate(images):
            if x.sum() == 0:
                continue
            x = self.year_models[index](x)
            score = x[-1]            
            year_scores.append(score)
        
        return torch.stack(year_scores, axis=1).mean(axis=1)
                
    

## Satellite Image-Segmentation for Flood-Damage Analysis
- This repo is for the reimplementation of a model made for segmenting satellite images for analyzing flood damages using publicly available images and data.

## Dataset

- **Free public images**: Sentinel dataset of Very High Resolution Images (1973 by 2263 pixels) with a resolution of .5m per pixel was used. Masks (960 by 960 pixels) with resolution of 1m per pixel were used for both building and damage detection.

- **Dataset** : [AAAI Harvey Data Link](https://s3.eu-central-1.amazonaws.com/corupublic/AAAI_harvey_data/harvey.zip)

### Sample Data 
<img src="https://github.com/orion29/Satellite-Image-Segmentation-for-Flood-Damage-Analysis/blob/main/Images/Image_vhr.png"/>


## Pre-processing steps
<li> VHR Images were downscaled to (1024,1024) resolution using BICUBIC resampling technique.</li>
<li> Image Masks were upsampled to (1024,1024) resolution using BICUBIC resampling technique.</li>
<li> Images and their respective Masks were cut into 4 patches of resolution (512,512) each.</li>
<li> Both VHR Images and Masks were converted from int tensor (0-255) to float tensor (0-1) and normalized using imagenet stats .</li><br>

- <ins>**BICUBIC Resampling**</ins> : Bicubic resampling computes new pixels using cubic splines. When upsampling, this method operates on the 4 by 4 cell of pixels surrounding each new pixel location. This is the recommended resampling method for most images as it represents a good trade-off between accuracy and speed.

## Image Patches
| Patches |
| ------------- |
| ![real1](https://github.com/AdiNarendra98/AI-for-Environment/blob/main/3.%20Satellite%20Image%20Segmentation%20for%20Flood%20Damage%20Analysis/Images/patches.png) |


## Training

- ### Model: <ins>UNET with Resnet-34 (pertained on Cifar-10 Imagenet Model) as a Backbone</ins>.
The <b> U-Net </b> is convolutional network architecture for fast and precise segmentation of images. It is an encoder-decoder style network.<br>
Using a U-Net with a pretrained resnet encoder means that the encoder part of the U-Net will be replaced by the resnet pretrained weights. It's a concept of transfer learning, i.e we don't need to train the model from scratch.<br>
<p align="center">
<img src="https://github.com/orion29/Satellite-Image-Segmentation-for-Flood-Damage-Analysis/blob/main/Images/unet.png" width="600">
</p> 

- ### Optimizer: <ins>ADAM</ins>

<b> Adaptive Moment Estimation (Adam) </b> is  an optimizer that computes adaptive learning rates for each parameter. In addition to storing an exponentially decaying average of past squared gradients vt like RMSprop, Adam also keeps an exponentially decaying average of past gradients mt, similar to momentum.
<li> gt =  Gradient Calculated </li>
<li> mt =  Momentum </li>
<li> vt =  RMSprop </li><br>
<img src="https://github.com/orion29/Satellite-Image-Segmentation-for-Flood-Damage-Analysis/blob/main/Images/moment.png" width="300">

- ### Scheduler: <ins>One Cycle Policy(3-Step Approach)</ins>
 <li>We progressively increase our learning rate from base_lr to lr_max and at the same time we progressively decrease our momentum from mom_max to mom_min.
 <li>We do the exact opposite: we progressively decrease our learning rate from lr_max to lr_max/div_factor and at the same time we progressively increase our momentum from mom_min to mom_max.
 <li>We further decrease our learning rate from lr_max/div_factor to lr_max/(div_factor x 100) and we keep momentum steady at mom_max.

<p align="center">
<img src="https://github.com/orion29/Satellite-Image-Segmentation-for-Flood-Damage-Analysis/blob/main/Images/onefit.png" width="600" height="300"><br>
</p>              			


## Training

#### <ins>Building Segmentation Training:</ins> 
**Validation Set Dice score(IOU)** : **0.86**

#### <ins>Damaged Area Segmentation Training</ins> 
Validaton Set Dice score(IOU) : **0.87**


## Predictions

|    **VHR Image(Input)**   |   **Generated Mask Image(Output)** |
|  ------------------------- | ---------------------------------- |
|  ![real1](https://github.com/orion29/Satellite-Image-Segmentation-for-Flood-Damage-Analysis/blob/main/Images/pred_img.png)             | ![real1](https://github.com/AdiNarendra98/AI-for-Environment/blob/main/3.%20Satellite%20Image%20Segmentation%20for%20Flood%20Damage%20Analysis/Images/pred.png)                  |


         
## Conclusion

- Used an **end-to-end trainable neural network architecture for multiresolution, multisensor, and multitemporal satellite images** and showed that it can perform **building footprint and flooded building segmentation tasks** and demonstrated that publicly available imagery alone can be used for effective segmentation of flooded buildings.
- Demonstrated approach is **applicable to different types of flood events** and could be **used to predict damage caused by other types of disasters**.
- It substantially **reduces the amount of time needed to produce flood maps** for first responders compared to current methods.

## Inspiration

- This model was inspired by the work by [**Kunal**](https://github.com/orion29/Satellite-Image-Segmentation-for-Flood-Damage-Analysis)

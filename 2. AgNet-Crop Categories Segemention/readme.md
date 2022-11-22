## Ag-Net: Crops Segmentation Model
- Ag-Net is a **bundle of customized deep neural networks for recognizing crops based on spectral characteristics**. The main idea is to customize the current neural networks like U-Net to make it more **suitable for extracting and recognizing the season-changing features of various crop over the growing season**. The ultimate **goal is to generate high-quality accurate crop maps at any stage of crops rather than waiting for next yea**r. 
- The training and validation ground truth data comes from **USGS EarthExplorer and USDA NASS**.
- This model was made as a part of the GSOC 2019 project by [Jensen Ziheng Sun](https://github.com/ZihengSun/Ag-Net),this code is a attempt for its re-implementation.

## Results

| **Original Ground Truth Image** | **Generated Mask Image** |
| ------------- | ------------- |
| ![real1](https://github.com/AdiNarendra98/AI-for-Environment/blob/main/2.%20AgNet-Crop%20Categories%20Segemention/Images/real2.png) | ![real1](https://github.com/AdiNarendra98/AI-for-Environment/blob/main/2.%20AgNet-Crop%20Categories%20Segemention/Images/pred1.png)  |
| ![real1](https://github.com/AdiNarendra98/AI-for-Environment/blob/main/2.%20AgNet-Crop%20Categories%20Segemention/Images/real1.png)  | ![pred2](https://github.com/AdiNarendra98/AI-for-Environment/blob/main/2.%20AgNet-Crop%20Categories%20Segemention/Images/pred2.png)  |
| ![real3](https://github.com/AdiNarendra98/AI-for-Environment/blob/main/2.%20AgNet-Crop%20Categories%20Segemention/Images/real3.png)  |  ![pred3](https://github.com/AdiNarendra98/AI-for-Environment/blob/main/2.%20AgNet-Crop%20Categories%20Segemention/Images/pred3.png)  |

## Dataset
- ### Agnet Dataset: [Link](https://github.com/ZihengSun/Ag-Net-Dataset)
- ### Color Map for Crops : [Link](https://github.com/ZihengSun/Ag-Net-Dataset/blob/master/colormap.py)

## Architecture Used and Modifications
- ### Basic Architecture- [**U-Net**](https://nn.labml.ai/unet/index.html)

- ### Modifications Made:
   * Use of **skip connections**.
   * Use of **GlobalMaxPool2D** instead of MaxPool2D.
   * Use of **Spatial Excitations**.
   * Use of **PRelu and Leaky Relu**.

<p align="center">
<img src="https://github.com/AdiNarendra98/AI-for-Environment/blob/main/2.%20AgNet-Crop%20Categories%20Segemention/Images/Model%20Modifications.png" width="350" height="350"><br>
<b>Modifications to Architecture</b><br>
</p>


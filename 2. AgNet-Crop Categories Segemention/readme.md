## Ag-Net: Crops Segmentation Model
- Ag-Net is a bundle of customized deep neural networks for recognizing crops based on spectral characteristics. The main idea is to customize the current neural networks like U-Net to make it more suitable for extracting and recognizing the season-changing features of various crop over the growing season. The ultimate goal is to generate high-quality accurate crop maps at any stage of crops rather than waiting for next year. The training and validation ground truth data comes from USGS EarthExplorer and USDA NASS.
- This model was made as a part of the GSOC 2019 project by [Jensen Ziheng Sun](https://github.com/ZihengSun/Ag-Net),this code is a attempt for its re-implementation.

## Results

| **Original Ground Truth Image** | **Generated Mask Image** |
| ------------- | ------------- |
| ![real1](https://github.com/AdiNarendra98/AI-for-Environment/blob/main/2.%20AgNet-Crop%20Categories%20Segemention/Images/real2.png) | ![real1](https://github.com/AdiNarendra98/AI-for-Environment/blob/main/2.%20AgNet-Crop%20Categories%20Segemention/Images/pred1.png)  |
| ![real1](https://github.com/AdiNarendra98/AI-for-Environment/blob/main/2.%20AgNet-Crop%20Categories%20Segemention/Images/real1.png)  | ![pred2](https://github.com/AdiNarendra98/AI-for-Environment/blob/main/2.%20AgNet-Crop%20Categories%20Segemention/Images/pred2.png)  |

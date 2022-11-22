## FloodNet-Semi-Supervised Classification and Segmentation on High Resolution Aerial Flood Images
  
- Re-Implementation of the paper [**Semi-Supervised Classification and Segmentation on High Resolution Aerial Images**](https://arxiv.org/abs/2105.08655).

## Results
- Check out the demo of the implementation on Streamlit Sharing:[**Demo Link**](https://share.streamlit.io/sahilkhose/floodnet/main/stream_app.py)

<p align="center">
<img src="https://github.com/AdiNarendra98/AI-for-Environment/blob/main/Paper%20Re-Implementations/05.FloodNet-Segmentation%20on%20High%20Quality%20Aerial%20Flood%20Images/Images/Pred1.png " width="800" height="400"><br>
<b>Sample Generated Predictions from various Tested Models</b><br>
</p>


## Dataset
- Used the **FloodNet Dataset**: [Download Link](https://github.com/BinaLab/FloodNet-Challenge-EARTHVISION2021)
- It is a high-resolution image dataset **acquired by a small UAV platform, DJI Mavic Pro quadcopters, after Hurricane Harvey**.
- These high resolution **(3000x4000x3) 2343 images** are accompanied by detailed semantic annotation regarding the damages.
- To advance the damage assessment process for post-disaster scenarios, the dataset provides a unique challenge considering **classification, semantic segmentation and visual question answering**.

<p align="center">
<img src="https://github.com/AdiNarendra98/AI-for-Environment/blob/main/Paper%20Re-Implementations/05.FloodNet-Segmentation%20on%20High%20Quality%20Aerial%20Flood%20Images/Images/Dataset.png " width="600" height="350"><br>
<b>FloodNet Dataset</b><br>
</p>


## Scripts and Functions

|       Notebooks                 |         Tasks             |
| --------------------------|:------------------------------:|
| [**FloodNet_T1.ipynb**](https://github.com/sahilkhose/FloodNet/blob/main/FloodNet_T1.ipynb)     | **Classification**                 |
| [**FloodNet_T2.ipynb**](https://github.com/sahilkhose/FloodNet/blob/main/FloodNet_T2.ipynb)     | **Segmentation**                   |
| [**Inference_Seg.ipynb**](https://github.com/sahilkhose/FloodNet/blob/main/Inference_Seg.ipynb)   | **Segmentation inference for Demo**|

## References
- [**FloodNet: A High Resolution Aerial Imagery Dataset for Post Flood Scene Understanding**](https://arxiv.org/abs/2012.02951) <a name="floodnet-cite"/>
- Blog Link for the Paper: [**Medium Link**](https://sahilkhose.medium.com/paper-presentation-e9bd0f3fb0bf)

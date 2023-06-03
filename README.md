# Color Harmonization

+ NTU CSIE 課程 ICG 2023 Term Project #13：Color Harmonization 之圖形使用者介面 Python 實作，含部分改進。作者：F09922184 許晉捷。
+ 2023 Spring, Iteractive Computer Graphics Term Project, F09922184 Chin-Chieh Hsu (許晉捷)
+ A third-party Python implementation with GUI of the paper **Color Harmonization** (https://dl.acm.org/doi/abs/10.1145/1179352.1141933) with user-friendly features and some refinement
+ Introduction to Color Harmonization (Google Slides):
    + https://docs.google.com/presentation/d/1flpqVetunF4u45N0L_M5hjcgTPlmym2C/edit?usp=sharing&ouid=108114821901174243032&rtpof=true&sd=true

# 貢獻

1. 第一個將此篇 paper 完整實作出來（網上找的到的 open source 都只有不完整的實作）。
1. 第一個結合 GUI（圖形使用者介面）的實作，含多項完整且細緻的功能。
    + 四種讀取影像的方法：from local, drag-and-drop（拖曳）, from URL, and from clipboard。
    + 針對每張影像提供 GUI 來調整參數設定。
    + 多執行緒（multithreading）執行演算法，不影響 GUI 操作。
    + 提供方便的原圖與結果的比較展示，效果如何一目瞭然。
    + 可方便快速地儲存色彩調和的結果至本機。
1. 可供 user 自行選擇 harmonic template type（七選一）；或是由程式自動尋找最佳的 template。
1. 結合 Super Resolution (SR) 技術，改善演算法執行效率問題。

# How to run

## Color Harmonization only (w/o Super Resolution)

*This has already realized all things in the original paper*

1. Use Python 3.8
1. ```git clone https://github.com/Rekkursion/ColorHarmonization_Qt.git```
1. ```cd ColorHarmonization_Qt```
1. Create and activate a virtual environment for Python 3.8 (optional, but recommended)
1. ```pip install -r requirements.txt```
1. Now one can already run the GUI by ```python main.py```, but without the feature of Super Resolution

## Color Harmonization w/ Super Resolution

*Reference: https://github.com/xinntao/Real-ESRGAN/*

7. Follow the first 5 steps listed above
1. ```git clone https://github.com/xinntao/Real-ESRGAN.git```
1. ```cd Real-ESRGAN```
1. ```pip install -r requirements.txt```
1. ```python setup.py develop```
1. ```cd ..```
1. Run the GUI by ```python main.py```, with the feature of Super Resolution activated

# Reference

+ Daniel Cohen-Or, Olga Sorkine, Ran Gal, Tommer Leyvand, Ying-Qing Xu, ACM SIGGRAPH, July 2006 (https://dl.acm.org/doi/abs/10.1145/1179352.1141933)
+ Y. Y. Boykov and M. . -P. Jolly, "Interactive graph cuts for optimal boundary & region segmentation of objects in N-D images," Proceedings Eighth IEEE International Conference on Computer Vision. ICCV 2001, Vancouver, BC, Canada, 2001, pp. 105-112 vol.1, doi: 10.1109/ICCV.2001.937505.
+ X. Wang, L. Xie, C. Dong and Y. Shan, "Real-ESRGAN: Training Real-World Blind Super-Resolution with Pure Synthetic Data," 2021 IEEE/CVF International Conference on Computer Vision Workshops (ICCVW), Montreal, BC, Canada, 2021, pp. 1905-1914, doi: 10.1109/ICCVW54120.2021.00217.


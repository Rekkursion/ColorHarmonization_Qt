# Color Harmonization

+ NTU CSIE 課程 ICG 2023 Term Project #13：Color Harmonization 之圖形使用者介面 Python 實作，含部分改進。作者：F09922184 許晉捷。
+ 2023 Spring, Iteractive Computer Graphics Term Project, F09922184 Chin-Chieh Hsu (許晉捷)
+ A third-party Python implementation with GUI of the paper **Color Harmonization** (https://dl.acm.org/doi/abs/10.1145/1179352.1141933) with user-friendly features and some refinement
+ Introduction to Color Harmonization (Google Slides):
    + https://docs.google.com/presentation/d/1flpqVetunF4u45N0L_M5hjcgTPlmym2C/edit?usp=sharing&ouid=108114821901174243032&rtpof=true&sd=true

# 程式 Demo 影片

https://youtu.be/Fd-HIYI_siQ

# 貢獻

1. 實作面
    1. 第一個將此篇 paper 完整實作出來（網上找的到的 open source 都只有不完整的實作）。
    1. 第一個結合 GUI（圖形使用者介面）的實作，含多項完整且細緻的功能。
        + 四種讀取影像的方法：from local, drag-and-drop（拖曳）, from URL, and from clipboard。
        + 針對每張影像提供 GUI 來調整參數設定。
        + 可套用另外的 reference image 當作色彩調和的基準。
        + 多執行緒（multithreading）執行演算法，不影響 GUI 操作。
        + 提供方便的原圖與結果的比較展示，效果如何一目瞭然。
        + 可方便快速地儲存色彩調和的結果至本機。
        + 可供 user 自行選擇 harmonic template type（七選一）；或是由程式自動尋找最佳的 template。
1. 算法面
    1. 結合 Super Resolution (SR) 技術，改善演算法執行效率問題。
    1. 結合前後景分割（image segmentation）技術，以前景的色調來調和背景；或以背景來調和前景。

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

1. Boykov, Y. Y., & Jolly, M.-P. (2001). Interactive graph cuts for optimal boundary & region segmentation of objects in ND images. Proceedings eighth IEEE international conference on computer vision. ICCV 2001, 
1. Cohen-Or, D., Sorkine, O., Gal, R., Leyvand, T., & Xu, Y.-Q. (2006). Color harmonization. In ACM SIGGRAPH 2006 Papers (pp. 624-630).
1. Matsuda, Y. 1995. Color design. Asakura Shoten.
1. Press, W. H., Teukolsky, S. A., Vetterling, W. T., & Flannery, B. P. (2007). Numerical recipes 3rd edition: The art of scientific computing. Cambridge university press. 
1. Rother, C., Kolmogorov, V., & Blake, A. (2004). " GrabCut" interactive foreground extraction using iterated graph cuts. ACM transactions on graphics (TOG), 23(3), 309-314. 
1. Tokumaru, M., Muranaka, N., & Imanishi, S. (2002). Color design support system considering color harmony. 2002 IEEE world congress on computational intelligence. 2002 IEEE international conference on fuzzy systems. FUZZ-IEEE'02. Proceedings (Cat. No. 02CH37291), 
1. Wang, X., Xie, L., Dong, C., & Shan, Y. (2021). Real-esrgan: Training real-world blind super-resolution with pure synthetic data. Proceedings of the IEEE/CVF International Conference on Computer Vision, 


# Implementation-Related Acknowledgement

+ Super Resolution: https://github.com/xinntao/Real-ESRGAN
+ PyQt5 Drag-and-drop: https://gist.github.com/peace098beat/db8ef7161508e6500ebe
+ PyQt5 Open a directory in the file explorer: https://stackoverflow.com/questions/6631299/python-opening-a-folder-in-explorer-nautilus-finder
+ Brent's method: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.brent.html#scipy.optimize.brent
+ Minimum-cut: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.flow.minimum_cut.html
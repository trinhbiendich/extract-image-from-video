# extract-image-from-video
extract image from video

### How to use

* Before pls install requirement module bay command
```bash
pip install -r requirements.txt
```
* and run bellow command to extract images from video
```bash
setup.py [-h] -p PATH -s SAVEPATH [-f FRAME] [-e EXTRACT] [-d DEBUG]
                [-t THRESHOLD] [-rd REMOVEDUPLICATE] [-max PERCENTSAME]
```
* Example :
```bash
python setup.py -p a.mp4 -f 11999 -t 50 -s C:\imgs\ -e True
```

#### Parameters

* `-p` or `--path` : path to input video path *`Require`*
* `-s` or `--savepath` : path of folder will save images *`Require`*
* `-f` or `--frame` : frame to start taken **default** is `0`
* `-e` or `--extract` : flag to enable extract images **default** `False` 
* `-d` or `--debug` : flag to enable show image **default** `False`
* `-t` or `--threshold` : focus measures that fall below this value will be considered 'blurry' **default** `60`
* `-rd` or `--removeduplicate` : flag to enable remove the same images **default** `False`
* `-max` or `--percentsame` : the ratio value between two images **default** `95%`

_**Note:**_ _Currently, the code support for MP4 and AVI only_

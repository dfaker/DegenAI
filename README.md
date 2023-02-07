# DegenAI
Degenerate AI Video Streamer

UI when paused searching for new segments:
![image](https://user-images.githubusercontent.com/35278260/217312195-82b8f0bb-70d7-4453-b4c7-19d01efa0212.png)

Selected scene samples from mainstream film and television:
![image-grid](https://user-images.githubusercontent.com/35278260/216857430-7d49f1c9-b2fd-4ad5-aa17-86769d7a5aa9.jpg)


Uses an aethetic predictor on top of [clip](https://github.com/openai/CLIP) as with [SD-Chad](https://github.com/grexzen/SD-Chad) but applies it to a folder of video files and plays any segments that pass a score threshold test.

Features fun pseudo VHS styled status messages.

When run on a dataset that contains it's preferred degenerate content and a threshold of 0.5, detections at the rate of 3 seconds of output video stream per one second of scan time easily filling the buffer for a constant curated stream, for mainstream datasets much lower acceptance rates are seen.

Provided with a pre-trained predictor that returns high predictions for frames that feature amongst other things:

- Female faces
- Heavy makeup looks
- Regions of human skin
- Open mouths
- Flesh coloured globules, particularly if oiled
- Feet
- Starfish
- Orchids
- Peaches
- Doo-Dahs, Tuppences, Fandangoes and Foofs
- Flesh coloured worms and snakes
- Generalised degeneracy

Requires libmpv, python-mpv, PIL, clip and torch. 

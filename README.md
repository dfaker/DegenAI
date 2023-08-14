# DegenAI
Degenerate AI Video Streamer

UI when paused searching for new segments:
![image](https://user-images.githubusercontent.com/35278260/217312881-ab8bf12c-2904-4865-8340-893b387b54a5.png)

Selected scene samples from mainstream film and television:
![image-grid](https://user-images.githubusercontent.com/35278260/216857430-7d49f1c9-b2fd-4ad5-aa17-86769d7a5aa9.jpg)

Uses an aethetic predictor on top of [clip](https://github.com/openai/CLIP) as with [SD-Chad](https://github.com/grexzen/SD-Chad) but applies it to a folder of video files and plays any segments that pass a score threshold test.

Features fun pseudo VHS styled status messages.

Requires libmpv, python-mpv, PIL, clip and torch. 

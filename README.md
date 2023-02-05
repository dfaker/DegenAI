# DegenAI
Artificial Video Cuts Editor

![image](https://user-images.githubusercontent.com/35278260/216849988-188fc56d-d0cb-4845-8fa8-fbe674963b93.png)

Uses an aethetic predictor on top of clip as with https://github.com/grexzen/SD-Chad but applies it to a folder of video files and plays any segments that pass a score threshold test.

Provided with a pre-trained predictor that returns high predictions for frame that feature amongst other things:

- Female faces
- Regions of human skin
- Open mouths
- Oiled globular surfaces
- Feet
- Flesh coloured worms and snakes

Requires libmpv, python-mpv, PIL and torch. 

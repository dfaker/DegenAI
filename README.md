# DegenAI
Artificial Video Cuts Editor

![image](https://user-images.githubusercontent.com/35278260/216849988-188fc56d-d0cb-4845-8fa8-fbe674963b93.png)

Uses an aethetic predictor on top of [clip](https://github.com/openai/CLIP) as with [SD-Chad](https://github.com/grexzen/SD-Chad) but applies it to a folder of video files and plays any segments that pass a score threshold test.

Features fun pseudo VHS styled status messages.

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

Requires libmpv, python-mpv, PIL, clip and torch. 

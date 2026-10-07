# Gesture-to-Voice: Hand Gesture Communication Aid

A Python application that recognises hand gestures through a webcam and speaks
them aloud, helping people with speech or hearing disabilities communicate
quickly with the people around them.

## 1. Problem Statement
People with speech impairments often struggle to express basic needs in public
places. Many people do not understand sign language, which creates a
communication gap. A low-cost system that turns simple gestures into spoken
words can reduce this gap.

## 2. Objectives
- Detect one or two hands in real time using an ordinary webcam.
- Recognise a set of 13 useful gestures.
- Convert each gesture into clear spoken English.
- Keep the system simple, offline and free to run.

## 3. Features
- Real-time hand tracking (21 landmarks per hand, up to 2 hands)
- 13 gestures mapped to everyday phrases, including a two-hand gesture
- Offline speech using the built-in Windows voice (no internet needed)
- Speaks every time a gesture is shown, and repeats every 5 seconds while it is held
- Stability filter: a gesture must be held briefly, so accidental movements are ignored
- Works with the left or right hand

## 4. Gesture Set

| Gesture | How to show it | Spoken phrase |
|---|---|---|
| Open palm | All five fingers up | "Hello" |
| Fist | Closed hand | "I need help" |
| Three fingers | Index, middle, ring up | "I need water" |
| Thumbs up | Only thumb out | "Yes" |
| Peace sign | Index and middle up | "No" |
| OK sign | Thumb and index tip touch, other fingers up | "Okay" |
| Shaka | Thumb and pinky out | "Take it easy" |
| Vulcan salute | Open hand, gap between middle and ring finger | "Live long and prosper" |
| Heart hands | Both hands form a heart | "Love and friendship" |
| Pinched fingers | All fingertips together, pointing up | "What do you want" |
| Sign of the horns | Index and pinky up, thumb tucked | "Rock on" |
| I love you | Thumb, index and pinky out | "I love you" |
| One finger up | Index finger only | "Come here" |

## 5. How It Works
1. **Capture**: OpenCV reads frames from the webcam.
2. **Detect**: MediaPipe Hands finds 21 landmark points on each hand.
3. **Classify**: the program checks which fingers are extended or folded, and measures distances between fingertips (for OK, pinched, Vulcan and heart gestures).
4. **Stabilise**: the same gesture must appear for 10 consecutive frames.
5. **Speak**: the phrase is read aloud with the Windows speech engine in a background thread, so the video never freezes. A held gesture repeats every 5 seconds.

## 6. Technologies Used
Python 3.9-3.11, OpenCV, MediaPipe, Windows System.Speech (via PowerShell)

## 7. Installation
```bash
git clone https://github.com/chiragsinghchiku15-lang/gesture-voice.git
cd gesture-voice
pip install -r requirements.txt
```

## 8. Usage
```bash
python signtosound.py
```
Hold a gesture in front of the camera for about half a second. The phrase appears on screen and is spoken aloud. Press **q** to quit.

## 9. Limitations
- Voice output works on Windows only (uses the built-in Windows speech engine).
- Needs good lighting and a hand fully visible to the camera.
- Complex gestures (Vulcan, pinched fingers, heart hands) are less reliable than simple ones.
- "Come here" is simplified to a single raised finger, not the beckoning motion.
- Rule-based, so it is not a full sign-language translator.
- English speech only.

## 10. Future Scope
- Train a machine-learning model to recognise a full sign-language alphabet.
- Add more languages (Hindi, etc.) and voices.
- Let users record and map their own gestures.
- Support macOS and Linux voices, and build a mobile or web version.

## 11. References
- MediaPipe Hands: https://developers.google.com/mediapipe/solutions/vision/hand_landmarker
- OpenCV: https://opencv.org

## Author
Chirag Singh
NSIT, Diploma CSE, 5th Semester

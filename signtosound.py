import math
import queue
import subprocess
import threading
import time

import cv2
import mediapipe as mp

# ---------- Settings ----------
HOLD_FRAMES = 10       # hold a gesture this many frames before it counts
REPEAT_SECONDS = 5.0   # repeat a held gesture every 5 seconds
RESET_FRAMES = 8       # frames with no gesture before it can speak again

# Finger pattern: (thumb, index, middle, ring, pinky)
GESTURES = {
    (1, 1, 1, 1, 1): "HELLO",    # open palm
    (0, 0, 0, 0, 0): "HELP",     # fist
    (0, 1, 1, 1, 0): "WATER",    # three fingers
    (1, 0, 0, 0, 0): "YES",      # thumbs up
    (0, 1, 1, 0, 0): "NO",       # peace sign
    (0, 1, 0, 0, 1): "HORNS",    # sign of the horns (thumb tucked)
    (1, 1, 0, 0, 1): "ILY",      # I love you (thumb, index, pinky)
    (1, 0, 0, 0, 1): "SHAKA",    # shaka (thumb and pinky)
    (0, 1, 0, 0, 0): "COME",     # one finger up = come here
}

PHRASES = {
    "HELLO": "Hello",
    "HELP": "I need help",
    "WATER": "I need water",
    "YES": "Yes",
    "NO": "No",
    "OK": "Okay",
    "SHAKA": "Take it easy",
    "VULCAN": "Live long and prosper",
    "HEART": "Love and friendship",
    "PINCHED": "What do you want",
    "HORNS": "Rock on",
    "ILY": "I love you",
    "COME": "Come here",
}


# ---------- Gesture detection ----------
def dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def hand_size(lm):
    return dist(lm[0], lm[9])   # wrist to middle-finger base


def finger_states(lm):
    states = []
    # Thumb: extended if tip is farther from pinky base than its joint
    states.append(1 if dist(lm[4], lm[17]) > dist(lm[3], lm[17]) else 0)
    # Other fingers: tip farther from the wrist than the middle joint
    # (works even if the hand is tilted or sideways)
    for tip, pip in zip((8, 12, 16, 20), (6, 10, 14, 18)):
        states.append(1 if dist(lm[0], lm[tip]) > dist(lm[0], lm[pip]) else 0)
    return states


def is_ok(lm, s):
    # thumb tip touches index tip, other three fingers extended
    return (dist(lm[4], lm[8]) < 0.35 * hand_size(lm)
            and s[2] == 1 and s[3] == 1 and s[4] == 1)


def is_pinched(lm):
    # all five fingertips gathered together, fingers pointing up
    hs = hand_size(lm)
    close = all(dist(lm[4], lm[t]) < 0.4 * hs for t in (8, 12, 16, 20))
    return close and lm[12].y < lm[9].y


def is_vulcan(lm):
    # open hand with a clear gap between middle and ring finger
    gap_mid_ring = dist(lm[12], lm[16])
    gap_idx_mid = dist(lm[8], lm[12])
    gap_ring_pinky = dist(lm[16], lm[20])
    return (gap_mid_ring > 1.6 * gap_idx_mid
            and gap_mid_ring > 1.6 * gap_ring_pinky)


def is_heart(a, b):
    # two hands: thumb tips touch and index tips touch
    hs = (hand_size(a) + hand_size(b)) / 2
    return dist(a[4], b[4]) < 0.5 * hs and dist(a[8], b[8]) < 0.7 * hs


def classify(hands):
    """hands = list of landmark lists (1 or 2 hands)."""
    if len(hands) == 2 and is_heart(hands[0], hands[1]):
        return "HEART"
    lm = hands[0]
    s = finger_states(lm)
    if is_pinched(lm):
        return "PINCHED"
    if is_ok(lm, s):
        return "OK"
    if s == [1, 1, 1, 1, 1] and is_vulcan(lm):
        return "VULCAN"
    return GESTURES.get(tuple(s))


# ---------- Speech: a fresh Windows voice process for every phrase ----------
class Speaker:
    def __init__(self):
        self.q = queue.Queue()
        threading.Thread(target=self.worker, daemon=True).start()

    def worker(self):
        while True:
            text = self.q.get()
            if text is None:
                break
            cmd = [
                "powershell", "-NoProfile", "-Command",
                "Add-Type -AssemblyName System.Speech; "
                "(New-Object System.Speech.Synthesis.SpeechSynthesizer)"
                f".Speak('{text}')",
            ]
            try:
                subprocess.run(cmd, creationflags=0x08000000)  # no popup window
            except Exception as e:
                print("Speech error:", e)

    def say(self, text):
        if self.q.qsize() < 2:
            self.q.put(text)

    def stop(self):
        self.q.put(None)


# ---------- Main program ----------
def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open the webcam.")
        return

    mp_hands = mp.solutions.hands
    drawing = mp.solutions.drawing_utils
    speaker = Speaker()

    candidate, count = None, 0
    last_spoken, last_time = None, 0.0
    none_count = 0
    shown = ""

    with mp_hands.Hands(max_num_hands=2,
                        min_detection_confidence=0.7,
                        min_tracking_confidence=0.6) as hands:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)
            result = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            gesture = None
            if result.multi_hand_landmarks:
                for h in result.multi_hand_landmarks:
                    drawing.draw_landmarks(frame, h, mp_hands.HAND_CONNECTIONS)
                gesture = classify([h.landmark for h in result.multi_hand_landmarks])

            # If no gesture for a few frames, reset so the next one speaks again
            if gesture is None:
                none_count += 1
                if none_count >= RESET_FRAMES:
                    last_spoken = None
            else:
                none_count = 0

            if gesture and gesture == candidate:
                count += 1
            else:
                candidate, count = gesture, (1 if gesture else 0)

            now = time.time()
            if candidate and count >= HOLD_FRAMES:
                shown = PHRASES[candidate]
                # speak at once, then repeat every 5 seconds while held
                if candidate != last_spoken or now - last_time >= REPEAT_SECONDS:
                    print("Speaking:", shown)
                    speaker.say(shown)
                    last_spoken, last_time = candidate, now
            elif not candidate:
                shown = ""

            cv2.rectangle(frame, (0, 0), (frame.shape[1], 50), (30, 42, 68), -1)
            cv2.putText(frame, shown or "Show a gesture...", (15, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.imshow("Gesture to Voice (press q to quit)", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    speaker.stop()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
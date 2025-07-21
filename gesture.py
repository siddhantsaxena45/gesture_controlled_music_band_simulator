import cv2
import mediapipe as mp
import pyautogui

def gesture_mouse_control(run_flag):
    screen_width, screen_height = pyautogui.size()
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
    mp_draw = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    clicking = False

    while run_flag["active"]:
        success, img = cap.read()
        if not success:
            continue

        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            lm_list = hand.landmark

            x = int(lm_list[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * screen_width)
            y = int(lm_list[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * screen_height)
            pyautogui.moveTo(x, y)

            index_tip = lm_list[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = lm_list[mp_hands.HandLandmark.THUMB_TIP]
            dx = abs(index_tip.x - thumb_tip.x)
            dy = abs(index_tip.y - thumb_tip.y)
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance < 0.03:
                if not clicking:
                    clicking = True
                    pyautogui.click()
            else:
                clicking = False

            mp_draw.draw_landmarks(img, hand, mp_hands.HAND_CONNECTIONS)

        cv2.imshow("Gesture Mouse Control", img)
       
        cv2.moveWindow("Gesture Mouse Control", 100, 300) 
        

        if cv2.waitKey(1) == 27: 
            break

    cap.release()
    cv2.destroyAllWindows()

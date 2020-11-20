#!/usr/bin/env python
# coding: utf-8

# In[1]:


import Mask_Monitoring
import Mask_Announce
import Mask_Detection
import cv2


# In[2]:


detec = Mask_Detection.Mask_Detection()


# In[3]:


cap = detec.create_Cam(0)

monitor = Mask_Monitoring.Mask_Monitoring()

while True:
    mask_check, img = detec.start_capture(cap)

    cv2.imshow('img', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    flag = monitor.maskCheck(mask_check, img)
        
    if flag == 1:
        announce = Mask_Announce.Mask_Announce()
        announce.passenger()
detec.cap_release(cap)
cv2.destroyAllWindows()


# In[ ]:





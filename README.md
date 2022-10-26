# Lind
A simple URL shortener

This python written url shortener is simple but complete in it's features. It only has two dependencies that you need to install and then you're ready to host it yourself. Some of the features:

- Simple, clean, user friendly design
- Lightweight to host but easily scalable to billions of links
- You can password protect Linds, let them expire at a certain time or limit the amount of times the Lind can be used
- You can manage a Lind after creation to edit the passwords or the underlying link by going to `{lind}/manage`
- Both a web-ui and api available
- A rate limiter available for creating Linds
- Easy to change how Lind behaves: you can change the minimum length or character range of the id's

The home screen where you can quickly make a simple Lind:
![image](https://user-images.githubusercontent.com/88994465/198064343-b2b8e13f-79ea-4034-9f54-172027f9c730.png)
Or use the advanced settings to add an expiration time, an usage limiter, password protect it or allow managing the Lind afterwards:
![image](https://user-images.githubusercontent.com/88994465/198064708-43e0a031-d9d8-4b7a-84c9-ff4d58578a7c.png)
Click `create` and you'll get the Lind:
![image](https://user-images.githubusercontent.com/88994465/198065108-4cfcec38-3efe-4295-b2ad-5643fabf117a.png)
When accessing a password-protected Lind, you'll first need to enter the password set when created in order to continue:
![image](https://user-images.githubusercontent.com/88994465/198065206-843dad20-0b13-4ce2-a868-886106e8776f.png)
If an admin password is given when creating a Lind, you can go to `{lind}/manage` to manage the Lind
![image](https://user-images.githubusercontent.com/88994465/198065369-ff3486f0-e1d3-4fc3-9a5e-db1be1ac2cb5.png)
![image](https://user-images.githubusercontent.com/88994465/198065422-fea77462-9b07-4ed9-aec5-bd9d5a4ba139.png)

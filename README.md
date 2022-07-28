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

The home screen:
![image](https://user-images.githubusercontent.com/88994465/181536708-7a04d22b-6a9e-41d9-ad54-7e3ae2c5f4c9.png)
Simply enter the url to get a lind:
![image](https://user-images.githubusercontent.com/88994465/181544937-c49d14e3-445e-4df5-8728-2618ca568ad1.png)
Or use the advanced settings to add an expiration time, an usage limiter, password protect it or allow managing the Lind afterwards:
![image](https://user-images.githubusercontent.com/88994465/181545554-031ecaa5-9dbe-4f40-95fb-1f20b9e095de.png)
Click `create` and you'll get the Lind:
![image](https://user-images.githubusercontent.com/88994465/180668116-971b066a-3fa7-41bc-8347-c7ff1aaec89d.png)
When accessing a password-protected Lind, you'll first need to enter the password set when created in order to continue:
![image](https://user-images.githubusercontent.com/88994465/180668135-61d2f4c6-b8c4-451d-9907-544b4babf9c3.png)
If an admin password is given when creating a Lind, you can go to `{lind}/manage` to manage the Lind
![image](https://user-images.githubusercontent.com/88994465/181064259-ff23975b-a893-404c-9393-0fdcaffeb016.png)
![image](https://user-images.githubusercontent.com/88994465/181543607-4705e288-3f6a-4f4f-8325-00ec43f61577.png)


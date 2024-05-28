import flet as ft
import asyncio
import websockets
import requests
import datetime
import json

with open('information.json') as fp:
    jd = json.load(fp)

class client:
    # ~~~~~ WS methods ~~~~~
    async def send_message(author,message):
        url = jd["WS address"] # server URL (ws protocol!)
        async with websockets.connect(url) as websocket:
            # await websocket.send(f"{author}: {message};")
            
            
            current_datetime = datetime.datetime.now()
            nowtime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
            dic = {"author": author, "content": message,"time":nowtime}
            data_string = json.dumps(dic)
            await websocket.send(data_string)
            result = requests.post(url=jd["Messages database"],json=dic)
            print(f"{author}: {message}; DB INFO : Code - {result.status_code}")
            
    async def connect_to_websocket(add_method,target):
        url = jd["WS address"] # server URL (ws protocol!)
        async with websockets.connect(url) as websocket:
            print("Connected to the WS server..")
            while True:
                response = await websocket.recv()
                end_index = response.find("'", 8)
                ip = response[7:end_index] #Sender ip
                print(f"Received response: {response}")
                ## add to page:
                # add_method(ft.Text(response))
                appendNewMessage(add_method,target,response)
                
    # ~~~~~ General methods ~~~~~
    def fixUrlLocation(base_url, i):
        # Check if the base URL already ends with '.json'
        if base_url.endswith('.json'):
          formatted_url = f"{base_url[:-5]}/{i}.json"  # Remove trailing '.json' and insert index
        else:
          formatted_url = f"{base_url}/{i}.json"

        return formatted_url
    
    # ~~~~~ DB methods ~~~~~
    def getDataFromDB():
        response = requests.get(jd["Messages database"])
        data = response.json()
        print("req made. Code :",response.status_code)
        return data
    
    def getUsersFromDB():
        url = jd["Users database"]
        response = requests.get(url)
        data = response.json()
        print("req made. Code :",response.status_code)
        return data
    
    def addUserToDB(username,password,image_url):
        url = jd["Users database"]
        response = requests.get(url)
        data = response.json()
        dict = {"username":username,"password":password,"level":"user","image":image_url}
        cnt = 0
        def is_url_image(image_url):
            try:
                image_formats = ("image/png", "image/jpeg", "image/jpg")
                r = requests.head(image_url)

                if r.headers["content-type"] in image_formats:
                   return True
                return False
            except:
                return False
                
        if (is_url_image(image_url=image_url) == False):
            return 422
        if (image_url == ""):
            del dict["image"]
        for i in data:
            if data[i]["username"] == username:
                return 409

        dict = {"username":username,"password":password,"level":"user","image":image_url}
        response = requests.post(url=url,json=dict)
        user_data = client.getUsersFromDB()
        return(response.status_code)
            
    def getOnlineUsers():
        url = jd["Online users database"]
        response = requests.get(url)
        data = response.json()
        print("req made. Code :",response.status_code)
        return data
    
    def setStatusOnline(user):
        
        lst = client.getUsersFromDB()
        current_datetime = datetime.datetime.now()
        nowtime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
        dic = {"username":user,"LoginTime":nowtime}
        response = requests.post(url = jd["Online users database"],json=dic)
        print("req made. Code : ",response.status_code)
    
    def setStatusOffline(user):
        users = client.getOnlineUsers()
        for i in users:
            if users[i]["username"] == user:
                n_url = client.fixUrlLocation(jd["Banned user database"],i)
                requests.delete(url = n_url)
    
    def banUser(username,reason,until):
        url = jd["Banned users database"]
        dict = {"username":username,"reason":reason,"until":until}
        response = requests.post(url=url,json=dict)
    
    def isUserBanned(username):
        url = jd["Banned users database"]
        response = requests.get(url=url)
        banned_users = response.json()
        current_datetime = datetime.datetime.now()
        nowtime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
        if (banned_users == None):
            return False
        for i in banned_users:
            if (username == banned_users[i]["username"]):
                if (nowtime < banned_users[i]["until"] ):
                    return True
        
        return False
    
    def pardonUser(username):
        url = jd["Banned users database"]
        response = requests.get(url=url)
        banned_users = response.json()
        for i in banned_users:
            if (username == banned_users[i]["username"]):
                n_url = client.fixUrlLocation(jd["Banned user database"],i)
                response = requests.delete(url = n_url)
                print(response.status_code)
        

def appendNewMessage(add_method,lv,payload):
    payload = json.loads(payload)
    message = payload["content"]
    author = payload["author"]
    local_level= "user"
    local_image = "https://static.vecteezy.com/system/resources/thumbnails/009/292/244/small/default-avatar-icon-of-social-media-user-vector.jpg"
    
    
    
    for j in user_data: #find user pfp
        if local_image == "https://static.vecteezy.com/system/resources/thumbnails/009/292/244/small/default-avatar-icon-of-social-media-user-vector.jpg":
            try:
                if user_data[j]['username'] == author: 
                    local_image = user_data[j]['image']
            except:
                print(f"image not found {author}")
    
    for j in user_data: # find user level
        if local_level == "user":
            try:
                if user_data[j]['username'] == author: 
                    local_level = user_data[j]['level']
            except:
                print(f"level not found {author}")
    
    levels = {"user":"red","admin":"yellow"}
    level_icon = {"user":None,"admin":"https://cdn-icons-png.flaticon.com/512/6941/6941697.png"}
    
    ls1 = [ #list without little icon next to the name
        ft.Image(local_image,border_radius=50,height=50,width=50),         # Display the profile picture in 50x50 format with rounded edges
        ft.Text(f"{author}",size=15,color=levels[local_level]), # Gets the message author name and color (based on level))
        ft.Text(f": {message}",size=15)                         # Adds the message content.
    ]
    
    ls2 = [ #list with little icon next to the name
        ft.Image(local_image,border_radius=50,height=50,width=50),        
        ft.Text(f"{author}",size=15,color=levels[local_level]),
        ft.Image(level_icon[local_level],width=15,height=15),              # Adds the user icon (e.g. crown for admin) *if theres one!*
        ft.Text(f": {message}",size=15)                        
    ]
    
    t1 = ft.IconButton(icon=ft.icons.DELETE, key=(author, message, payload["time"]), on_click=lambda e: deleteMessage(lv, e))
    if (login_level == "admin"):
        ls1.insert(1,t1)
        ls2.insert(1,t1)
    
    rw = ft.Row()
    if (level_icon[local_level]) != None:
        rw = ft.Row(ls2)
    elif (level_icon[local_level]) == None:
        rw = ft.Row(ls1)    
        
    lv.controls.append(rw)
    add_method(lv)

def updateMenuButton(level):
    global mb
    print("given level : ",level)
    if (level == "admin"):
        mb = ft.PopupMenuButton(items=[
            ft.PopupMenuItem(icon=ft.icons.DELETE,text="Delete",on_click=lambda _:deleteMessage)
        ])
    else:
        mb = ft.PopupMenuButton(items=[
            ft.PopupMenuItem(text="I am NOT an admin")
        ])

def deleteMessage(lv, e):
    author, content, time = e.control.key
    for i in data:
        if data[i]["author"] == author:
            if data[i]["content"] == content:
                if data[i]["time"] == time:
                    n_url = client.fixUrlLocation(jd["Messages database"],i)
                    result = requests.delete(n_url)
                    if result.status_code == 200:
                        # Remove the corresponding control from the ListView
                        for control in lv.controls:
                            if isinstance(control, ft.Row):
                                for child in control.controls:
                                    if isinstance(child, ft.IconButton):
                                        if child.key == (author, content, time):
                                            lv.controls.remove(control)
                                            lv.update()
                                            break
                    print(f"Request status code: {result.status_code}")

           
user_data = client.getUsersFromDB()              
data = client.getDataFromDB()
login_level = ""
tbar = ft.AppBar()

async def main(page: ft.Page):
    def checkAdminStatus():
        if (login_level == "admin"):
            userListSetup()
            page.go("/panel")
            page.update()
        else:
            print("Error! not")
    
    async def on_button_click(button):
        await client.send_message(local_name,tf1.value)
    
    def checkSignIn(username,password):
        user_data = client.getUsersFromDB()
        for i in user_data:
            if username == user_data[i]['username']:
                if password == user_data[i]['password']:
                    global login_level
                    global local_name 
                    login_level = user_data[i]['level']
                    local_name = user_data[i]['username']
                    updateMenuButton(user_data[i]['level'])
                    client.setStatusOnline(local_name)
                    page.update()
                    init_setup()
                    page.go("/chat")
                    
                    
                else:
                    print("erroring")
                    l_tb2.error_text = "Username or password incorrect."
                    page.update()
            else:
                l_tb2.error_text = "Username or password incorrect."
                page.update()
    
    def online_setup():
        online_users = client.getOnlineUsers()
        name = ""
        pfp_url = "https://static.vecteezy.com/system/resources/thumbnails/009/292/244/small/default-avatar-icon-of-social-media-user-vector.jpg"
        global user_data
        for i in online_users:
            c_user = online_users[i]["username"]
            for j in user_data:
                if (c_user == user_data[j]["username"]):
                    name = user_data[j]["username"]
                    if "image" in user_data[j]:
                        pfp_url = user_data[j]["image"]
                    else:
                        pass
            
            pfp = ft.Stack(
                [
                    ft.CircleAvatar(
                        foreground_image_url=pfp_url,
                        height=120,
                        width=120
                    ),
                    ft.Container(
                        content=ft.CircleAvatar(bgcolor=ft.colors.GREEN, radius=15),
                        alignment=ft.alignment.bottom_left,
                    ),
                ],
                width=120,
                height=120,
            )
            levels = {"user":"red","admin":"yellow"}
            t = ft.Column(controls=[
                ft.Text(f"{name} - {login_level}",size=36,font_family="https://raw.githubusercontent.com/google/fonts/master/ofl/kanit/Kanit-Bold.ttf",color = levels[login_level]),
                ft.Text("Lorem ipsum dolor sit amet, consectetur adipiscing elit. In vel massa dignissim, dictum enim eu, blandit turpis. Sed tincidunt orci eu placerat sodales. Morbi porta facilisis eros, eu scelerisque lacus feugiat at. Sed convallis, metus nec tristique rutrum, lectus enim consequat ipsum, non ultrices orci turpis in justo. Maecenas et diam tellus. Ut eget posuere felis. Pellentesque est leo, auctor sed ligula a, pellentesque laoreet urna. Nulla at venenatis diam. Curabitur nec tellus nulla. Vivamus turpis magna, suscipit id imperdiet tempor, tristique sed magna. ",width=400)
            ])
            ls = ft.Row([pfp,t])
            o_lv.controls.append(ls)
            page.update()
                            
    def init_setup():
        for i in data:
            message = data[i]
            local_level= "user"
            local_image = "https://static.vecteezy.com/system/resources/thumbnails/009/292/244/small/default-avatar-icon-of-social-media-user-vector.jpg"
            for j in user_data:
                if local_image == "https://static.vecteezy.com/system/resources/thumbnails/009/292/244/small/default-avatar-icon-of-social-media-user-vector.jpg":
                    try:
                        if user_data[j]['username'] == message['author']: 
                            local_image = user_data[j]['image']
                    except:
                        pass
            
            for j in user_data:
                if local_level == "user":
                    try:
                        if user_data[j]['username'] == message['author']: 
                            local_level = user_data[j]['level']
                    except:
                        print(f"level not found {message['author']}")
            
            levels = {"user":"red","admin":"yellow"}
            level_icon = {"user":None,"admin":"https://cdn-icons-png.flaticon.com/512/6941/6941697.png"}
            
            t1 = ft.IconButton(icon=ft.icons.DELETE, key=(message['author'], message['content'], message['time']), on_click=lambda e: deleteMessage(lv, e))
            
            
            ls1 = [ #list without little icon next to the name
                ft.Image(local_image,border_radius=50,height=50,width=50),         # Display the profile picture in 50x50 format with rounded edges
                ft.Text(f"{message['author']}",size=15,color=levels[local_level]), # Gets the message author name and color (based on level))
                ft.Text(f": {message['content']}",size=15)                         # Adds the message content.
            ]
            
            ls2 = [ #list with little icon next to the name
                ft.Image(local_image,border_radius=50,height=50,width=50),        
                ft.Text(f"{message['author']}",size=15,color=levels[local_level]),
                ft.Image(level_icon[local_level],width=15,height=15),              # Adds the user icon (e.g. crown for admin) *if theres one!*
                ft.Text(f": {message['content']}",size=15)                        
            ]
            
            
            
            if (login_level == "admin"):
                ls1.insert(1,t1)
                ls2.insert(1,t1)
            
            rw = ft.Row()
            if (level_icon[local_level]) != None:
                rw = ft.Row(ls2)
            elif (level_icon[local_level]) == None:
                rw = ft.Row(ls1)    
                
            
            lv.controls.append(rw)

    def close_window():
        page.window_destroy()
        client.setStatusOffline(local_name)
    
    def onlinePeoplePage():
        online_setup()
        page.go("/online")
        
    def signUp():
        s = client.addUserToDB(s_username.value,s_password.value,s_imgurl.value)
        
        if (s == 200):
            page.go("/login")
        elif (s == 409):
            s_username.error_text = ("Username taken")
            page.update()
        elif (s == 422):
            s_imgurl.error_text = "Image format invalid (Use [PNG/JPG/JPEG/GIF/SVG])"
            page.update()
        else:
            s_username.error_text = ("Something went wrong")
            page.update()
    
    def userListSetup():
        # bannedUsers = 
        global user_data
        for i in user_data:
            name = user_data[i]["username"]
            if "image" in user_data[i]:
                image = user_data[i]["image"]
            else:
                image = "https://static.vecteezy.com/system/resources/thumbnails/009/292/244/small/default-avatar-icon-of-social-media-user-vector.jpg"
            pfp = ft.CircleAvatar(foreground_image_url=image,height=100,width=100)
            t = ft.Text(name)
            
            def ban_user(e):
                print("ban ",e.control.key)
            col = ft.Column(controls=[
                t,
                ft.FilledButton("Ban",on_click=ban_user)
            ])
            ls = ft.Row([pfp,col])
            a_lv.controls.append(ls)
            page.update()
            
    def chatDisconnect():
        lv.controls.clear()
        client.setStatusOffline(local_name)
        page.go("/login")
        
    bar_items = [
        ft.PopupMenuItem(text="Online people", on_click=lambda _:onlinePeoplePage()),
        ft.PopupMenuItem(text="Admin panel",on_click=lambda _:checkAdminStatus())
    ]
    f = ft.PopupMenuButton(
            icon=ft.icons.MORE_HORIZ,
            items=bar_items,
    )
    tf1 = ft.TextField(hint_text="Your message..")
    lv = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
    tbar = ft.AppBar(title=ft.Text("Welcome"), bgcolor="#603A28",automatically_imply_leading=False,actions=[
        f,
        ft.IconButton(ft.icons.LOGOUT,tooltip="Logout",on_click=lambda _:chatDisconnect()),
        ft.IconButton(icon=ft.icons.CLOSE,tooltip="Close window",on_click=lambda _:close_window()),
    ])
    p1 = [
            tbar,
            lv,  
            tf1,
            ft.ElevatedButton("Send", on_click=on_button_click), 
    ]
    
    l_tbar = ft.AppBar(title=ft.Text("Sign in"), bgcolor="#603A28",actions=[ft.IconButton(icon=ft.icons.CLOSE,tooltip="Close window",on_click=lambda _:page.window_destroy())])
    l_tb1 = ft.TextField(label="username",multiline=False)
    l_tb2 = ft.TextField(label="password",multiline=False,password=True, can_reveal_password=True)
    l_b = ft.TextButton(text="Sign in",on_click=lambda _:checkSignIn(l_tb1.value,l_tb2.value))
    p2 = [
        l_tbar,
        l_tb1,
        l_tb2,
        ft.Row([l_b,ft.TextButton("Signup",on_click=lambda _:page.go("/signup"))]),
    ]
    page.window_frameless = True
    
    
    a_lv = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=False)
    p3 = [a_lv,
          ft.TextButton(text="Back",on_click=lambda _: page.go("/chat"))]
    
    
    o_lv = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
    p4 = [ft.Text("Online people:"),
          o_lv,
          ft.IconButton(icon=ft.icons.DOOR_BACK_DOOR,on_click=lambda _:page.go("/chat"))]
    
    s_username = ft.TextField(hint_text="Username...")
    s_password = ft.TextField(hint_text="Password...",password=True, can_reveal_password=True)
    s_imgurl = ft.TextField(hint_text="Enter URL of your image")
    s_lst = ft.Column(controls=[
        ft.Text("Sign up"),
        s_username,
        s_password,
        s_imgurl,
        ft.Row(controls=[ft.TextButton("Sign up",on_click=lambda _:signUp()),ft.TextButton(text="Back",on_click=lambda _: page.go("/login"))])
    ])
    s_cont = ft.Container(alignment="center",content=[s_lst])
    p5 = [s_lst]
    
    
    def route_change(e):
        page.views.clear()
        page.views.append(
            ft.View(
                "/login",
                p2,
                bgcolor="#402315"
            )
        )
        if page.route == "/chat":
            page.views.append(
                ft.View(
                    "/chat",
                    p1,
                    bgcolor="#402315"
                )
            ) 
        elif page.route == "/panel":
            page.views.append(
                ft.View(
                    "/panel",
                    p3
                )
            )
        elif page.route == "/online":
            page.views.append(
                ft.View(
                    "/online",
                    p4
                )
            )
        elif page.route == "/signup":
            page.views.append(
                ft.View(
                    "/signup",
                    p5,
                )
            )
        page.update()
    
    def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.go(page.route)
    
    await client.connect_to_websocket(page.add,lv)

def run():
    ft.app(main)
    
if __name__ == "__main__":
    run()

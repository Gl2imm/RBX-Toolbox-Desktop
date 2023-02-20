import os
import sys
import requests
import time
import csv
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
from datetime import datetime
import webbrowser
import logging


######## VARS ########
cookie = None
ver = "Beta_1"
logging.basicConfig(filename="logfile.log", level=logging.INFO)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    tlbx_path = os.path.dirname(sys.executable)
    test = 0
elif __file__:
    test = 1
    tlbx_path = os.path.dirname(__file__)



#tlbx_path = os.path.dirname(__file__) Dont use this
logging.info(tlbx_path)

#icon_path = "icon.ico"
if test == 0:
    icon = resource_path(r'icon.ico')
else:
    icon_path = "icon.ico"
    icon = os.path.join(tlbx_path, icon_path)
num = 1

data = {"S/N":[],"Name":[],"favoriteCount":[],"price":[],"Sales":[],"id":[],"assetType":[],"RBX Earned (30%)":[],"DevEx (USD)":[]} #For CSV Write
csv_lst = []
UserOwnGrps = [] #Groups, ID and Members
#UserOwnGrpsLst = [] #Pure group names


csv_fldr = os.path.join(tlbx_path, 'CSV Files')
if not os.path.exists(csv_fldr):
    os.makedirs(csv_fldr)

logging.info(csv_fldr)

date = datetime.today().strftime('%d-%m-%Y')

button = "q"

stop = False
def onkeypress(event):
    global stop
    if event.name == button:
        stop = True

#https://create.roblox.com/docs/studio/catalog-api
rbx_sort_type = {
    '0':'Relevance',
    '1':'MostFavorited',
    '2':'Bestselling',
    '3':'RecentlyUpdated',
    '4':'PriceLowToHigh',
    '5':'PriceHighToLow'
}

#https://create.roblox.com/docs/reference/engine/enums/AssetType
rbx_ast_type = {
    '2':'T-Shirt',
    '8':'Hat',
    '11':'Shirt',
    '12':'Pants',
    '17':'Head',
    '18':'Face',
    '19':'Gear',
    '25':'Arms',
    '26':'Legs',
    '27':'Torso',
    '28':'RightArm',
    '29':'LeftArm',
    '30':'LeftLeg',
    '31':'RightLeg',
    '41':'HairAccessory',
    '42':'FaceAccessory',
    '43':'NeckAccessory',
    '44':'ShoulderAccessory',
    '45':'FrontAccessory',
    '46':'BackAccessory',
    '47':'WaistAccessory',
    '48':'ClimbAnimation',
    '49':'DeathAnimation',
    '50':'FallAnimation',
    '51':'IdleAnimation',
    '52':'JumpAnimation',
    '53':'RunAnimation',
    '54':'SwimAnimation',
    '55':'WalkAnimation',
    '56':'PoseAnimation',
    '61':'EmoteAnimation',
    '62':'Video',
    '64':'TShirtAccessory',
    '65':'ShirtAccessory',
    '66':'PantsAccessory',
    '67':'JacketAccessory',
    '68':'SweaterAccessory',
    '69':'ShortsAccessory',
    '70':'LeftShoeAccessory',
    '71':'RightShoeAccessory',
    '72':'DressSkirtAccessory',
    '73':'FontFamily',
    '76':'EyebrowAccessory',
    '77':'EyelashAccessory',
    '78':'MoodAnimation',
    '79':'DynamicHead'
    }

#################


######## Tkinter #########
#https://epydoc.sourceforge.net/stdlib/Tkinter.Misc-class.html#update
root = tk.Tk()
root.title(f'Login || Ver. {ver}')
window_width = 280
window_height = 140
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int(screen_width/2 - window_width / 2)
center_y = int(screen_height/2 - window_height / 2)
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
root.resizable(False, False)
root.iconbitmap(icon)
label = tk.Label(root,text="Paste Cookie Value here:")
label.pack(fill='x', expand=True)
entry = tk.Entry()
entry.pack(fill='x', expand=True, padx=10)
entry.focus()

def update_label(label_warn):
    label_warn.pack_forget()
    label_warn["text"]="ERROR: Field is Empty!!!"
    label_warn.pack()

def login_clicked(entry):
    global cookie
    cookie = entry.get()

    if cookie == "":
        update_label(label_warn)
    else:
        global session
        session = requests.Session()
        session.cookies[".ROBLOSECURITY"] = cookie
        req = rbx_request("POST", "https://auth.roblox.com/") #Check Authorization (200)
        print(req)
        create_main_window(root)
    
        
button = ttk.Button(root ,text='Login',command=lambda: login_clicked(entry))
button.pack(expand=True, pady=10)

label_note = tk.Label(root,text="Note. Pls wait after you press 'Login', \nToolbox will fetch user data")
label_note.pack(fill='x', expand=True)

label_warn = tk.Label(root,text="",fg="#FF0000")
label_warn.pack(fill='x', expand=True)
label_warn.focus()
################################

#Authorised request
def rbx_request(method, url, **kwargs):
    request = session.request(method, url, **kwargs)
    logging.info(f"1st Request: {request.status_code}")
    method = method.lower()
    if method in ["post", "put", "patch", "delete"]:
        if "X-CSRF-TOKEN" in request.headers:
            session.headers["X-CSRF-TOKEN"] = request.headers["X-CSRF-TOKEN"]
            if request.status_code == 403:  # Request failed, send it again
                request = session.request(method, url, **kwargs)
                logging.info(f"2nd Request: {request.status_code}")
    return request
#req = rbx_request("POST", "https://auth.roblox.com/") #Check Authorization (200)


#Get User from Session
def get_user():
    global UserId
    global UserName
    global UserDispName
    request = rbx_request("GET","https://users.roblox.com/v1/users/authenticated") #Check Which user is authorized
    UserInfo = request.json()
    UserId = UserInfo.get("id")
    UserName = UserInfo.get("name")
    UserDispName = UserInfo.get("displayName")
    #print("Auth Status: ", req.status_code)
    print(f"You are Authorized as: {UserName}")


#Groups that user is in
def get_groups():
    request = requests.get(f"https://groups.roblox.com/v1/users/{UserId}/groups/roles")
    UserGrpsInfo = request.json()
    for i in UserGrpsInfo["data"]:
        GrpInfo = i.get('group')
        GrpName = GrpInfo.get('name')
        GrpId = GrpInfo.get('id')
        GrpMembers = GrpInfo.get('memberCount')
        GrpOwnerInfo = GrpInfo.get('owner')
        GrpOwner = GrpOwnerInfo.get('userId')
        #UserOwnGrps.append({"id": GrpId, "name": GrpName, "memberCount": GrpMembers})
        if UserId == GrpOwner:
            #pass
            UserOwnGrps.append({"id": GrpId, "name": GrpName, "memberCount": GrpMembers})



#Item request
def itms_req(url,cat_ctgr,NextPageCursor,GROUP_ID,sel_srt):
    #https://create.roblox.com/docs/studio/catalog-api
    #https://catalog.roblox.com/v1/search/items/details?Category=3&CreatorType=2&CreatorTargetId=7902286&limit=10
    if NextPageCursor == None:
        response = requests.get(url, 
        params={
            "Category": cat_ctgr,
            "CreatorType": 2, 
            "CreatorTargetId": GROUP_ID, 
            "limit": 30,
            "SortType": sel_srt
            })
    else:
        response = requests.get(url, 
        params={
            "Category": cat_ctgr,
            "CreatorType": 2, 
            "CreatorTargetId": GROUP_ID, 
            "limit": 30,
            "SortType": sel_srt,
            "cursor": NextPageCursor
            })
    rbx_itms = response.json()
    return rbx_itms


def update_status(status):
    label_stats.grid_forget()
    label_stats["text"]=status
    label_stats.grid(column=2, row=13, columnspan=4, sticky=tk.EW, padx=5, pady=5)
    label_stats.update()

#Loop all items in request
def loop_items(rbx_itms,cat_ctgr,NextPageCursor,name_to_print,GROUP_ID,sel_srt):
    global num
    status = f"Checking {name_to_print}. Please Wait ..."
    print(status)
    logging.info(f"Checking {name_to_print} started with: \ncat_ctgr:{cat_ctgr},\nNextPageCursor:{NextPageCursor},\nname_to_print:{name_to_print},\nGROUP_ID:{GROUP_ID},\nsel_srt:{sel_srt}")
    update_status(status)
    for i in rbx_itms["data"]:
        itm_name = i.get('name')
        itm_favs = i.get('favoriteCount')
        itm_price = i.get('price')
        itm_id = i.get('id')
        itm_type = i.get('assetType')
        itm_type = rbx_ast_type[str(itm_type)]
        response = rbx_request(
                    "GET",
                    f"https://api.roblox.com/marketplace/productinfo?assetId={itm_id}"
                )
        itm_info = response.json()
        itm_sales = itm_info['Sales']
        itm_desc = itm_info['Description']

        #print(f"{num}. {itm_name}; Favorites: {itm_favs}; Price: {itm_price}; Sales: {itm_sales}; ID: {itm_id}; assetType: {itm_type}")

        itm_name = f'=HYPERLINK("https://www.roblox.com/catalog/{itm_id}", "{itm_name}")' #Clickable link for CSV

        #MATH
        itm_rbx = itm_price * itm_sales * 0.3 
        itm_devx = itm_rbx / 50000 * 175

        csv_lst.append({"S/N": num, "Name": itm_name, "favoriteCount": itm_favs, "price": itm_price, "Sales": itm_sales, "id": itm_id, "assetType": itm_type, "RBX Earned (30%)": itm_rbx, "DevEx (USD)": itm_devx})
        num += 1
    while NextPageCursor != None:
        rbx_itms = itms_req(f"https://catalog.roblox.com/v1/search/items/details",cat_ctgr,NextPageCursor,GROUP_ID,sel_srt)
        NextPageCursor = rbx_itms.get("nextPageCursor")
        for i in rbx_itms["data"]:
            itm_name = i.get('name')
            itm_favs = i.get('favoriteCount')
            itm_price = i.get('price')
            itm_id = i.get('id')
            itm_type = i.get('assetType')
            itm_type = rbx_ast_type[str(itm_type)]
            response = rbx_request(
                        "GET",
                        f"https://api.roblox.com/marketplace/productinfo?assetId={itm_id}"
                    )
            itm_info = response.json()
            itm_sales = itm_info['Sales']
            itm_desc = itm_info['Description']

            #print(f"{num}. {itm_name}; Favorites: {itm_favs}; Price: {itm_price}; Sales: {itm_sales}; ID: {itm_id}; assetType: {itm_type}")

            itm_name = f'=HYPERLINK("https://www.roblox.com/catalog/{itm_id}", "{itm_name}")' #Clickable link for CSV

            #MATH
            itm_rbx = itm_price * itm_sales * 0.3 
            itm_devx = itm_rbx / 50000 * 175

            csv_lst.append({"S/N": num, "Name": itm_name, "favoriteCount": itm_favs, "price": itm_price, "Sales": itm_sales, "id": itm_id, "assetType": itm_type, "RBX Earned (30%)": itm_rbx, "DevEx (USD)": itm_devx})
            num += 1



#Accessories Check
def get_accessories(GROUP_ID,sel_srt):
    cat_ctgr = 11
    rbx_itms = itms_req(f"https://catalog.roblox.com/v1/search/items/details",cat_ctgr,None,GROUP_ID,sel_srt)
    NextPageCursor = rbx_itms.get("nextPageCursor")
    loop_items(rbx_itms,cat_ctgr,NextPageCursor,"Accessories",GROUP_ID,sel_srt)


def get_clothing(GROUP_ID,sel_srt):
#Clothing Check
    cat_ctgr = 3
    rbx_itms = itms_req(f"https://catalog.roblox.com/v1/search/items/details",cat_ctgr,None,GROUP_ID,sel_srt)
    NextPageCursor = rbx_itms.get("nextPageCursor")
    loop_items(rbx_itms,cat_ctgr,NextPageCursor,"Clothing",GROUP_ID,sel_srt)


def exp_csv(sel_grp):
    csv_file = os.path.join(csv_fldr, sel_grp + f"_Sales Data_{date}.csv")
    sum = [{"S/N": "", "Name": "", "favoriteCount": "", "price": "", "Sales": f'=SUM(E2:E{len(csv_lst) + 1})'}]
    status = "Writing to CSV ..."
    update_status(status)
    header = data.keys()

    try:
        with open(csv_file, 'w', encoding='UTF8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            writer.writerows(csv_lst)
            writer.writerows(sum)
        status = "CSV write Completed ..."
    except OSError as err:
        if err.errno == 13:
            status = "Unable to open the CSV file. If you opened it - close and try again"
        else:
           status = f"Something Went wrong while open CSV file. Erron Number: {err.errno}"
        print(err.errno, err.strerror) 
    update_status(status)
    print(status)
'''
   print err            - [Errno 2] No such file or directory: 'hello'
   print err.errno      - 2
   print err.strerror   - No such file or directory
   print err.filename   - hello
'''

'''
response = rbx_request(
    "GET",
    f"https://groups.roblox.com/v1/groups/{GROUP_ID}/audit-log",
    params={
        "actionType": "SpendGroupFunds", # Optional parameter
        #"userId": 12345, # Optional parameter
        "sortOrder": "Asc", # Optional parameter
        "limit": 10, # Optional parameter
        #"cursor": "2_1_30f7a44e7a6552e7a299b959305e2df8" # Optional parameter
})
print("Responce Status: ", response.status_code)
audit_logs = response.json()
#print(audit_logs)

for i in audit_logs["data"]:
        print(i.get('description')['ItemDescription'])

#for log in audit_logs .data:
    #print(f"{log.actor.user.username} | {log.actionType}")

'''




#403 Token Validation Failed
#401 Authorization has been denied for this request


'''
grp_usr_num = 0
grp_limit = 10  #10, 25, 50, 100
grp_id = 7902286  # Group ID

keyboard.on_press(onkeypress)

grp_req = requests.get(f"https://groups.roblox.com/v1/groups/{grp_id}/users?{grp_limit}=10&sortOrder=Asc")
grp_data = grp_req.json()
for i in grp_data["data"]:
    print('User (' + str(grp_usr_num) + '): ' + i.get('user')['username'] + ' (' + i.get('user')['displayName'] + ')')
    grp_usr_num += 1

NextPageCursor = grp_data["nextPageCursor"]

while NextPageCursor != None:
    grp_req = requests.get(f"https://groups.roblox.com/v1/groups/7902286/users?limit={grp_limit}&cursor={NextPageCursor}&sortOrder=Asc")
    grp_data = grp_req.json()
    NextPageCursor = grp_data["nextPageCursor"]
    #print(NextPageCursor)
    #time.sleep(1)
    for i in grp_data["data"]:
        grp_usr_num += 1
        print('User (' + str(grp_usr_num) + '): ' + i.get('user')['username'] + ' (' + i.get('user')['displayName'] + ')')
    time.sleep(1)
    if stop:
        print("stopped")
        break


#print(grp_data)
#print("Next page:", grp_data["nextPageCursor"])
#print("Next page:", grp_data["data"], "\n")
'''

def create_main_window(root):
    root.destroy()
    root = tk.Tk()
    root.title(f'RBX Toolbox (Desktop) || Ver. {ver}')
    #root.geometry('600x400+50+50') widthxheight±x±y

    #Create Root Window
    window_width = 420
    window_height = 225
    # get the screen dimension
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    # find the center point
    center_x = int(screen_width/2 - window_width / 2)
    center_y = int(screen_height/2 - window_height / 2)
    # set the position of the window to the center of the screen
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    # place a label on the root window
    root.resizable(False, False)
    root.iconbitmap(icon)



    # configure the grid
    #https://www.pythontutorial.net/tkinter/tkinter-grid/
    
    root.grid_rowconfigure(1, weight = 0, minsize = 5, pad = 0)
    root.grid_rowconfigure(2, weight = 0, minsize = 10, pad = 0)
    root.grid_rowconfigure(3, weight = 0, minsize = 10, pad = 0)
    root.grid_rowconfigure(4, weight = 0, pad = 0)
    root.grid_rowconfigure(5, weight = 0, pad = 0)
    root.grid_rowconfigure(6, weight = 0, pad = 0)
    root.grid_rowconfigure(7, weight = 0, pad = 0)
    root.grid_rowconfigure(8, weight = 0, minsize = 10, pad = 0)
    root.grid_rowconfigure(9, weight = 0, pad = 0)
    root.grid_rowconfigure(10, weight = 0, minsize = 15, pad = 0)
    root.grid_rowconfigure(11, weight = 0, minsize = 15, pad = 0)
    root.grid_rowconfigure(12, weight = 0, minsize = 15, pad = 0)
    root.grid_rowconfigure(13, weight = 0, pad = 0)
    root.grid_rowconfigure(14, weight = 0, pad = 0)
    root.grid_columnconfigure(1, weight = 0, minsize = 5, pad = 0)
    root.grid_columnconfigure(2, weight = 1, pad = 0)
    root.grid_columnconfigure(3, weight = 3, pad = 0)
    root.grid_columnconfigure(4, weight = 1, pad = 0)
    root.grid_columnconfigure(5, weight = 2, pad = 0)
    root.grid_columnconfigure(6, weight = 0, minsize = 5, pad = 0)


    get_user()
    get_groups()

    #MenuUserGroups = ", ".join(UserOwnGrpsLst)
    message = tk.Label(root, text=f"Logged in as: {UserName}")
    message.grid(column=2, row=2, columnspan=2, sticky=tk.W, padx=5, pady=5)

    ############### GROUP SELECT ###############
    def use_selected_grp(Grpvar,Sortvar):
        global num
        sel_grp = Grpvar.get()
        sel_srt = Sortvar.get()
        logging.info(f"Button Export clicked with: sel_grp:{sel_grp}; sel_srt:{sel_srt}")
        for key, value in rbx_sort_type.items():
            if sel_srt == value:
                sel_srt = key
                print(f"Selected Sorting: {sel_srt} - {value}")
                break
        for group in UserOwnGrps:
            if group["name"] == sel_grp:
                GROUP_ID = group["id"]
                print(f"Selected Group ID: {GROUP_ID}")
                break
        get_accessories(GROUP_ID,sel_srt)
        get_clothing(GROUP_ID,sel_srt)
        exp_csv(sel_grp)
        csv_lst.clear()
        num = 1

    grp_label = tk.Label(root, text="Select Group:")
    grp_label.grid(column=2, row=6, sticky=tk.S, padx=5, pady=5)

    Grpchoices = []
    for GrpName in UserOwnGrps:
        Grpchoices.append(GrpName.get("name"))
    Grpvar = tk.StringVar()
    Grpvar.set(Grpchoices[0])

    grps_dropdown = ttk.Combobox(root, textvariable=Grpvar, values=Grpchoices)
    grps_dropdown.grid(column=3, row=6, sticky=tk.EW, padx=5, pady=5)
    

    ############### SORTING SELECT ###############
    message = tk.Label(root, text=f"Sort by:")
    message.grid(column=4, row=6, sticky=tk.S, padx=5, pady=5)

    Sortchoices = []
    for i in range(len(rbx_sort_type)):
        Sortchoices.append(rbx_sort_type.get(str(i)))
    Sortvar = tk.StringVar()
    Sortvar.set(Sortchoices[0])

    sort_dropdown = ttk.Combobox(root, textvariable=Sortvar, values=Sortchoices)
    sort_dropdown.grid(column=5, row=6, sticky=tk.EW, padx=5, pady=5)
    #sel_sort = str({i for i in rbx_sort_type if rbx_sort_type[i]==sel_sort})
    

    ############### BUTTON EXPORT ###############
    csv_button = ttk.Button(root,text='Export CSV',command=lambda: use_selected_grp(Grpvar,Sortvar))
    csv_button.grid(column=2, row=9, columnspan=2, sticky=tk.W, padx=5, pady=5)
    
    
    #test_button = ttk.Button(root,text='Test',command=lambda: exp_csv(sel_grp))
    #test_button.grid(column=3, row=1, columnspan=2, padx=5, pady=5)
    #test_button2 = ttk.Button(root,text='Test',command=lambda: print(var_get(Grpvar)))
    #test_button2.grid(column=3, row=11, columnspan=2, padx=5, pady=5)

    global label_stats
    label_stats = tk.Label(root, text="Ready ...", bg="#FFFFFF")
    label_stats.grid(column=2, row=13, columnspan=4, sticky=tk.EW, padx=5, pady=5)
    #label_stats.focus()



    #################### Discord Link ####################
    def link(url):
        webbrowser.open_new(url)

    link1 = tk.Label(root, text="RBX Toolbox (Desktop) discord", cursor="hand2")
    link1.bind("<Button-1>", lambda e: link("https://discord.gg/gFa4mY7"))
    link1.grid(column=2, row=14, columnspan=4, sticky=tk.SW, padx=5, pady=5)

    #Link Color
    def on_enter(e):
        link1['foreground'] = '#0000FF'

    def on_leave(e):
        link1['foreground'] = 'black'

    link1.bind("<Enter>", on_enter)
    link1.bind("<Leave>", on_leave)
    ####################

# keep the window displaying
root.mainloop()


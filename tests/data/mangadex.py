from tests.helpers.utils import Response

def failed_call():
    return Response("", 500)

def oneshot():
    return Response("""
    {"manga":{"cover_url":"\/images\/manga\/48696.png?1589307458","description":"","
title":"Love Live! Sunshine!! - A Manual for Capturing a Fallen Angel
(Doujinshi)","artist":"Azuma Yuki, Ooshima Tomo","author":"Azuma Yuki, Ooshima T
omo","status":2,"genres":[7,21,38],"last_chapter":"0","lang_name":"Japanese","la
ng_flag":"jp","hentai":0,"links":null},"chapter":{"891363":{"volume":"","chapter
":"","title":"Oneshot","lang_code":"gb","group_id":1,"group_name":"Doki Fansubs"
,"group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestam
p":1589470260}},"group":{"1":{"group_name":"Doki Fansubs"}},"status":"OK"}
""", 200)

# 34 pages
def oneshot_chapter():
    return Response("""
    {"id":891363,"timestamp":1589470260,"hash":"57ddcf004d54e9decc74285b1e5e72f1",
"volume":"","chapter":"","title":"Oneshot","lang_name":"English","lang_code":"gb",
"manga_id":48696,"group_id":1,"group_id_2":0,"group_id_3":0,"comments":4,"server":
"https:\/\/mangadex.org\/data\/","page_array":["s1.png","s2.png","s3.png","s4.png"
,"s5.png","s6.png","s7.png","s8.png","s9.png","s10.png","s11.png","s12.png","s13.p
ng","s14.png","s15.png","s16.png","s17.png","s18.png","s19.png","s20.png","s21.png
","s22.png","s23.png","s24.png","s25.png","s26.png","s27.png","s28.png","s29.png",
"s30.png","s31.png","s32.png","s33.png","s34.png"],"long_strip":0,"status":"OK"}
""", 200)

# 18 pages
def decimal_chapter():
    return Response("""
    {"id":314099,"timestamp":1526259335,"hash":"fda9034a6141bb73a9839a4abadea6ca",
"volume":"1","chapter":"1.5","title":"I'm Bad With Gals (Part 2)","lang_name":"Eng
lish","lang_code":"gb","manga_id":26208,"group_id":12,"group_id_2":0,"group_id_3":
0,"comments":6,"server":"https:\/\/s5.mangadex.org\/data\/","page_array":["T1.jpg"
,"T2.jpg","T3.jpg","T4.jpg","T5.jpg","T6.jpg","T7.jpg","T8.jpg","T9.jpg","T10.jpg"
,"T11.jpg","T12.jpg","T13.jpg","T14.jpg","T15.jpg","T16.jpg","T17.jpg","T18.jpg"],
"long_strip":0,"status":"OK"}
""", 200)

# 3 pages
def normal_chapter():
    return Response("""
    {"id":799199,"timestamp":1581005084,"hash":"2999d227ffebb78cd5a8d7523f686cad",
"volume":"","chapter":"10","title":"","lang_name":"English","lang_code":"gb","mang
a_id":44999,"group_id":4419,"group_id_2":0,"group_id_3":0,"comments":23,"server":"
https:\/\/s5.mangadex.org\/data\/","page_array":["M1.png","M2.png","M3.png"],"long
_strip":0,"status":"OK"}
""", 200)

def decimal_chapters():
    return Response("""
    {"manga":{"cover_url":"\/images\/manga\/26208.jpg?1536260405","description":"&qu
ot;They do not care even if I can see their panties!&quot;     High school
student Daisuke Kaji, who is bad with gals, was made to deliver something to the
house of the biggest monster gal, Chiriko Iega. Forced to bring Iega to her
bedroom Kaji is shocked by her unimaginably filthy room! After being amazed by
the level of cleaning knowledge Kaji demonstrated Iega extorts him into cleaning
her entire room!    The beginning of a gal love
comedy!","title":"Gal☆Cleaning!","artist":"Ramunemura
Shuwata","author":"Ramunemura Shuwata","status":3,"genres":[5,8,9,11,23,24,50],"
last_chapter":"10","lang_name":"Japanese","lang_flag":"jp","hentai":0,"links":{"
al":"101683","ap":"gal-cleaning","bw":"series\/163847","kt":"40938","mu":"147069
","amz":"https:\/\/www.amazon.co.jp\/dp\/B07DCQL5S2\/","cdj":"http:\/\/www.cdjap
an.co.jp\/product\/NEOBK-2229129","ebj":"https:\/\/www.ebookjapan.jp\/ebj\/45905
8\/","mal":"112661","raw":"https:\/\/pocket.shonenmagazine.com\/episode\/1393201
6480029828543"}},"chapter":{"526576":{"volume":"2","chapter":"10","title":"The
Runaway Gal?","lang_code":"gb","group_id":12,"group_name":"\/a\/nonymous","group
_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1548
292521},"596674":{"volume":"2","chapter":"10","title":"Убегающая девушка?","lang
_code":"ru","group_id":7908,"group_name":"Rusyak","group_id_2":0,"group_name_2":
null,"group_id_3":0,"group_name_3":null,"timestamp":1556220447},"518525":{"volum
e":"2","chapter":"9","title":"She’s a gal but...","lang_code":"gb","group_id":12
,"group_name":"\/a\/nonymous","group_id_2":0,"group_name_2":null,"group_id_3":0,
"group_name_3":null,"timestamp":1547258743},"596673":{"volume":"2","chapter":"9"
,"title":"Она гяру, но...","lang_code":"ru","group_id":7908,"group_name":"Rusyak
","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timesta
mp":1556220402},"508326":{"volume":"2","chapter":"8.99","title":"I (?) Gals","la
ng_code":"gb","group_id":12,"group_name":"\/a\/nonymous","group_id_2":0,"group_n
ame_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1546059720},"596672":
{"volume":"2","chapter":"8.99","title":"Я (?) гяру","lang_code":"ru","group_id":
7908,"group_name":"Rusyak","group_id_2":0,"group_name_2":null,"group_id_3":0,"gr
oup_name_3":null,"timestamp":1556220327},"499408":{"volume":"2","chapter":"8.98"
,"title":"Do you like gals?","lang_code":"gb","group_id":12,"group_name":"\/a\/n
onymous","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"
timestamp":1544724597},"596671":{"volume":"2","chapter":"8.98","title":"Тебе
нравятся гяру?","lang_code":"ru","group_id":7908,"group_name":"Rusyak","group_id
_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1556220
287},"493685":{"volume":"2","chapter":"8.97","title":"Kaede Tokimura’s Memories 
(4)","lang_code":"gb","group_id":12,"group_name":"\/a\/nonymous","group_id_2":0,
"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1543798144},"
596669":{"volume":"2","chapter":"8.97","title":"Воспоминания Каеды Токимуры (4)"
,"lang_code":"ru","group_id":7908,"group_name":"Rusyak","group_id_2":0,"group_na
me_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1556220236},"485770":{
"volume":"2","chapter":"8.96","title":"Kaede Tokimura’s Memories (3)","lang_code
":"gb","group_id":12,"group_name":"\/a\/nonymous","group_id_2":0,"group_name_2":
null,"group_id_3":0,"group_name_3":null,"timestamp":1542507890},"596667":{"volum
e":"2","chapter":"8.96","title":"Воспоминания Каеды Токимуры (3)","lang_code":"r
u","group_id":7908,"group_name":"Rusyak","group_id_2":0,"group_name_2":null,"gro
up_id_3":0,"group_name_3":null,"timestamp":1556220194},"484453":{"volume":"2","c
hapter":"8.95","title":"Kaede Tokimura’s Memories (2)","lang_code":"gb","group_i
d":12,"group_name":"\/a\/nonymous","group_id_2":0,"group_name_2":null,"group_id_
3":0,"group_name_3":null,"timestamp":1542345573},"596665":{"volume":"2","chapter
":"8.95","title":"Воспоминания Каеды Токимуры (2)","lang_code":"ru","group_id":7
908,"group_name":"Rusyak","group_id_2":0,"group_name_2":null,"group_id_3":0,"gro
up_name_3":null,"timestamp":1556220094},"477199":{"volume":"2","chapter":"8.94",
"title":"Kaede Tokimura’s Memories","lang_code":"gb","group_id":12,"group_name":
"\/a\/nonymous","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3"
:null,"timestamp":1541301416},"596664":{"volume":"2","chapter":"8.94","title":"В
оспоминания Каеды Токимуры","lang_code":"ru","group_id":7908,"group_name":"Rusya
k","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timest
amp":1556220021},"466773":{"volume":"2","chapter":"8.93","title":"The Class with
the Pantyless Gal (7)","lang_code":"gb","group_id":12,"group_name":"\/a\/nonymou
s","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timest
amp":1540054206},"596663":{"volume":"2","chapter":"8.93","title":"Класс с
девушкой без трусиков (7)","lang_code":"ru","group_id":7908,"group_name":"Rusyak
","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timesta
mp":1556219921},"459064":{"volume":"2","chapter":"8.92","title":"The Class with
the Pantyless Gal (6)","lang_code":"gb","group_id":12,"group_name":"\/a\/nonymou
s","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timest
amp":1538696065},"596657":{"volume":"2","chapter":"8.92","title":"Класс с
девушкой без трусиков (6)","lang_code":"ru","group_id":7908,"group_name":"Rusyak
","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timesta
mp":1556219781},"452843":{"volume":"2","chapter":"8.91","title":"The Class with
the Pantyless Gal (5)","lang_code":"gb","group_id":12,"group_name":"\/a\/nonymou
s","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timest
amp":1537664112},"596653":{"volume":"2","chapter":"8.91","title":"Класс с
девушкой без трусиков (5)","lang_code":"ru","group_id":7908,"group_name":"Rusyak
","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timesta
mp":1556219676},"444503":{"volume":"2","chapter":"8.9","title":"The Class with
the Pantyless Gal (4)","lang_code":"gb","group_id":12,"group_name":"\/a\/nonymou
s","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timest
amp":1536199856},"596652":{"volume":"2","chapter":"8.9","title":"Класс с
девушкой без трусиков (4)","lang_code":"ru","group_id":7908,"group_name":"Rusyak
","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timesta
mp":1556219613},"436363":{"volume":"2","chapter":"8.8","title":"The Class with
the Pantyless Gal (3)","lang_code":"gb","group_id":12,"group_name":"\/a\/nonymou
s","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timest
amp":1535073406},"596651":{"volume":"2","chapter":"8.8","title":"Класс с
девушкой без трусиков (3)","lang_code":"ru","group_id":7908,"group_name":"Rusyak
","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timesta
mp":1556219575},"426919":{"volume":"2","chapter":"8.7","title":"The Class with
the Pantyless Gal (2)","lang_code":"gb","group_id":12,"group_name":"\/a\/nonymou
s","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timest
amp":1534101488},"596650":{"volume":"2","chapter":"8.7","title":"Класс с
девушкой без трусиков (2)","lang_code":"ru","group_id":7908,"group_name":"Rusyak
","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timesta
mp":1556219533},"416316":{"volume":"2","chapter":"8.6","title":"The Class with
the Pantyless Gal","lang_code":"gb","group_id":12,"group_name":"\/a\/nonymous","
group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp"
:1532652063},"596649":{"volume":"2","chapter":"8.6","title":"Класс с девушкой
без трусиков (1)","lang_code":"ru","group_id":7908,"group_name":"Rusyak","group_
id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":15562
19487},"415104":{"volume":"2","chapter":"8.5","title":"Gals and Going to School"
,"lang_code":"gb","group_id":12,"group_name":"\/a\/nonymous","group_id_2":0,"gro
up_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1532483803},"5966
48":{"volume":"2","chapter":"8.5","title":"Гяру и поход в школу","lang_code":"ru
","group_id":7908,"group_name":"Rusyak","group_id_2":0,"group_name_2":null,"grou
p_id_3":0,"group_name_3":null,"timestamp":1556219396},"415103":{"volume":"1","ch
apter":"8","title":"Gal and the End of...","lang_code":"gb","group_id":12,"group
_name":"\/a\/nonymous","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_
name_3":null,"timestamp":1532483771},"624673":{"volume":"1","chapter":"8","title
":"","lang_code":"br","group_id":4913,"group_name":"Alley Cat's Scan","group_id_
2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":15589302
45},"596647":{"volume":"1","chapter":"8","title":"Гяру и конец...","lang_code":"
ru","group_id":7908,"group_name":"Rusyak","group_id_2":0,"group_name_2":null,"gr
oup_id_3":0,"group_name_3":null,"timestamp":1556219338},"410044":{"volume":"1","
chapter":"7","title":"A Gal’s Devotion ♡ Then, a sudden...","lang_code":"gb","gr
oup_id":12,"group_name":"\/a\/nonymous","group_id_2":0,"group_name_2":null,"grou
p_id_3":0,"group_name_3":null,"timestamp":1531629744},"611159":{"volume":"1","ch
apter":"7","title":"","lang_code":"br","group_id":4913,"group_name":"Alley Cat's
Scan","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"tim
estamp":1557697678},"596646":{"volume":"1","chapter":"7","title":"Внезапная ❤
преданность гяру...","lang_code":"ru","group_id":7908,"group_name":"Rusyak","gro
up_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":15
56219301},"405961":{"volume":"1","chapter":"6","title":"The Gal That Changes
Clothes at Shibuya?!","lang_code":"gb","group_id":12,"group_name":"\/a\/nonymous
","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timesta
mp":1531018513},"611154":{"volume":"1","chapter":"6","title":"","lang_code":"br"
,"group_id":4913,"group_name":"Alley Cat's Scan","group_id_2":0,"group_name_2":n
ull,"group_id_3":0,"group_name_3":null,"timestamp":1557697580},"598981":{"volume
":"1","chapter":"6","title":"Gal itu menggati pakaiannya di
shibuya","lang_code":"id","group_id":5912,"group_name":"Pedo Scans","group_id_2"
:0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1556471387
},"596645":{"volume":"1","chapter":"6","title":"Дечонки покупают одежду в Сибуя?
!","lang_code":"ru","group_id":7908,"group_name":"Rusyak","group_id_2":0,"group_
name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1556219242},"402706"
:{"volume":"1","chapter":"5","title":"Gals and Meals and... Panties?!","lang_cod
e":"gb","group_id":12,"group_name":"\/a\/nonymous","group_id_2":0,"group_name_2"
:null,"group_id_3":0,"group_name_3":null,"timestamp":1530767431},"611151":{"volu
me":"1","chapter":"5","title":"","lang_code":"br","group_id":4913,"group_name":"
Alley Cat's Scan","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_
3":null,"timestamp":1557697468},"527568":{"volume":"1","chapter":"5","title":"Ga
ls, Sarapan, dan Celana
Dalam...?!","lang_code":"id","group_id":5912,"group_name":"Pedo Scans","group_id
_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1548419
915},"596644":{"volume":"1","chapter":"5","title":"Гяру, Еда и....Трусики?!","la
ng_code":"ru","group_id":7908,"group_name":"Rusyak","group_id_2":0,"group_name_2
":null,"group_id_3":0,"group_name_3":null,"timestamp":1556219196},"355904":{"vol
ume":"1","chapter":"4","title":"The Night The Gal Cosplayed...","lang_code":"gb"
,"group_id":12,"group_name":"\/a\/nonymous","group_id_2":0,"group_name_2":null,"
group_id_3":0,"group_name_3":null,"timestamp":1528644841},"611150":{"volume":"1"
,"chapter":"4","title":"","lang_code":"br","group_id":4913,"group_name":"Alley
Cat's Scan","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":nul
l,"timestamp":1557697355},"526288":{"volume":"1","chapter":"4","title":"Cosplay
Apa yang dikenakan si Gal Pada Malam
Hari?","lang_code":"id","group_id":5912,"group_name":"Pedo Scans","group_id_2":0
,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1548252742},
"596643":{"volume":"1","chapter":"4","title":"Ночь гяру косплея...","lang_code":
"ru","group_id":7908,"group_name":"Rusyak","group_id_2":0,"group_name_2":null,"g
roup_id_3":0,"group_name_3":null,"timestamp":1556219141},"329775":{"volume":"1",
"chapter":"3","title":"Gals really are...","lang_code":"gb","group_id":12,"group
_name":"\/a\/nonymous","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_
name_3":null,"timestamp":1527137359},"611146":{"volume":"1","chapter":"3","title
":"","lang_code":"br","group_id":4913,"group_name":"Alley Cat's Scan","group_id_
2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":15576972
54},"520646":{"volume":"1","chapter":"3","title":"Gadis Gal itu benar-
benar....","lang_code":"id","group_id":5912,"group_name":"Pedo Scans","group_id_
2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":15474896
84},"596641":{"volume":"1","chapter":"3","title":"Девчонки такие...","lang_code"
:"ru","group_id":7908,"group_name":"Rusyak","group_id_2":0,"group_name_2":null,"
group_id_3":0,"group_name_3":null,"timestamp":1556219086},"327300":{"volume":"1"
,"chapter":"2","title":"Living with a Gal","lang_code":"gb","group_id":12,"group
_name":"\/a\/nonymous","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_
name_3":null,"timestamp":1526937390},"442981":{"volume":"1","chapter":"2","title
":"","lang_code":"br","group_id":4913,"group_name":"Alley Cat's Scan","group_id_
2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":15359931
08},"520644":{"volume":"1","chapter":"2","title":"Tinggal dengan Gadis
Gal","lang_code":"id","group_id":5912,"group_name":"Pedo Scans","group_id_2":0,"
group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1547489599},"5
96640":{"volume":"1","chapter":"2","title":"Жизнь с девушкой","lang_code":"ru","
group_id":7908,"group_name":"Rusyak","group_id_2":0,"group_name_2":null,"group_i
d_3":0,"group_name_3":null,"timestamp":1556219006},"314099":{"volume":"1","chapt
er":"1.5","title":"I'm Bad With Gals (Part 2)","lang_code":"gb","group_id":12,"g
roup_name":"\/a\/nonymous","group_id_2":0,"group_name_2":null,"group_id_3":0,"gr
oup_name_3":null,"timestamp":1526259335},"424415":{"volume":"1","chapter":"1.5",
"title":"","lang_code":"br","group_id":4913,"group_name":"Alley Cat's Scan","gro
up_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":15
33702213},"596639":{"volume":"1","chapter":"1.5","title":"Ненависть к гяру
(Часть 2)","lang_code":"ru","group_id":7908,"group_name":"Rusyak","group_id_2":0
,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1556218933},
"291112":{"volume":"1","chapter":"1","title":"I'm Bad with Gals (Part 1)","lang_
code":"gb","group_id":12,"group_name":"\/a\/nonymous","group_id_2":0,"group_name
_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1525401133},"292812":{"v
olume":"1","chapter":"1","title":"Soy malo con las Gals","lang_code":"mx","group
_id":534,"group_name":"IkkiFansub","group_id_2":0,"group_name_2":null,"group_id_
3":0,"group_name_3":null,"timestamp":1525448724},"407632":{"volume":"1","chapter
":"1","title":"","lang_code":"br","group_id":4913,"group_name":"Alley Cat's Scan
","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timesta
mp":1531215048},"521171":{"volume":"1","chapter":"1,5","title":"Aku buruk dengan
Gal..","lang_code":"id","group_id":5912,"group_name":"Pedo Scans","group_id_2":0
,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1547568169},
"519146":{"volume":"1","chapter":"1","title":"chapter
01","lang_code":"id","group_id":5912,"group_name":"Pedo Scans","group_id_2":0,"g
roup_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1547315904},"59
6638":{"volume":"1","chapter":"1","title":"Ненависть к гяру (Часть 1)","lang_cod
e":"ru","group_id":7908,"group_name":"Rusyak","group_id_2":0,"group_name_2":null
,"group_id_3":0,"group_name_3":null,"timestamp":1556218776},"328196":{"volume":"
1","chapter":"0","title":"Chiriko Iega the Gal!","lang_code":"gb","group_id":12,
"group_name":"\/a\/nonymous","group_id_2":0,"group_name_2":null,"group_id_3":0,"
group_name_3":null,"timestamp":1527050342},"362532":{"volume":"1","chapter":"0",
"title":"","lang_code":"br","group_id":4913,"group_name":"Alley Cat's Scan","gro
up_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":15
28855756},"515336":{"volume":"1","chapter":"0","title":"chapter
00","lang_code":"id","group_id":5912,"group_name":"Pedo Scans","group_id_2":0,"g
roup_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1546790375},"59
6637":{"volume":"1","chapter":"0","title":"Гяру Чирико Иега!","lang_code":"ru","
group_id":7908,"group_name":"Rusyak","group_id_2":0,"group_name_2":null,"group_i
d_3":0,"group_name_3":null,"timestamp":1556218682}},"group":{"12":{"group_name":
"\/a\/nonymous"},"7908":{"group_name":"Rusyak"},"4913":{"group_name":"Alley 
Cat's Scan"},"5912":{"group_name":"Pedo 
Scans"},"534":{"group_name":"IkkiFansub"}},"status":"OK"}
""", 200)


def normal_series():
    return Response("""
 {"manga":{"cover_url":"\/images\/manga\/44999.png?1588592628","description":"[b
]Links:[\/b]  [*][url=https:\/\/www.pixiv.net\/en\/users\/19735227]Author's 
Pixiv[\/url]  [*][url=https:\/\/twitter.com\/os_fresa]Author's 
Twitter[\/url]","title":"Nei and Souta's Petite Manga","artist":"os_fresa","auth
or":"os_fresa","status":1,"genres":[5,9,23,31,60,76],"last_chapter":"0","lang_na
me":"Japanese","lang_flag":"jp","hentai":0,"links":{"kt":"56295","mu":"162148"}}
,"chapter":{"891033":{"volume":"","chapter":"60","title":"","lang_code":"gb","gr
oup_id":4419,"group_name":"Tabunne Scans","group_id_2":0,"group_name_2":null,"gr
oup_id_3":0,"group_name_3":null,"timestamp":1589447908},"889141":{"volume":"","c
hapter":"59","title":"","lang_code":"gb","group_id":4419,"group_name":"Tabunne S
cans","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"tim
estamp":1589297861},"887427":{"volume":"","chapter":"58","title":"","lang_code":
"gb","group_id":4419,"group_name":"Tabunne Scans","group_id_2":0,"group_name_2":
null,"group_id_3":0,"group_name_3":null,"timestamp":1589150706},"883709":{"volum
e":"","chapter":"57","title":"","lang_code":"gb","group_id":4419,"group_name":"T
abunne Scans","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":n
ull,"timestamp":1588954155},"881641":{"volume":"","chapter":"56","title":"","lan
g_code":"gb","group_id":4419,"group_name":"Tabunne Scans","group_id_2":0,"group_
name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1588795325},"880526"
:{"volume":"","chapter":"55","title":"","lang_code":"gb","group_id":4419,"group_
name":"Tabunne Scans","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_n
ame_3":null,"timestamp":1588700320},"875559":{"volume":"","chapter":"54","title"
:"","lang_code":"gb","group_id":4419,"group_name":"Tabunne Scans","group_id_2":0
,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1588272830},
"873116":{"volume":"","chapter":"53","title":"","lang_code":"gb","group_id":4419
,"group_name":"Tabunne Scans","group_id_2":0,"group_name_2":null,"group_id_3":0,
"group_name_3":null,"timestamp":1588020617},"873113":{"volume":"","chapter":"52.
5","title":"Announcement and 
Corrections","lang_code":"gb","group_id":4419,"group_name":"Tabunne Scans","grou
p_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":158
8020556},"865960":{"volume":"","chapter":"52","title":"","lang_code":"gb","group
_id":4419,"group_name":"Tabunne Scans","group_id_2":0,"group_name_2":null,"group
_id_3":0,"group_name_3":null,"timestamp":1587498106},"862630":{"volume":"","chap
ter":"51","title":"","lang_code":"gb","group_id":4419,"group_name":"Tabunne Scan
s","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timest
amp":1587235491},"877182":{"volume":"","chapter":"51","title":"","lang_code":"fr
","group_id":7367,"group_name":"Kawaii desu desu","group_id_2":0,"group_name_2":
null,"group_id_3":0,"group_name_3":null,"timestamp":1588436646},"862629":{"volum
e":"","chapter":"50","title":"","lang_code":"gb","group_id":4419,"group_name":"T
abunne Scans","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":n
ull,"timestamp":1587235448},"876374":{"volume":"","chapter":"50","title":"","lan
g_code":"fr","group_id":7367,"group_name":"Kawaii desu desu","group_id_2":0,"gro
up_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1588361264},"8603
75":{"volume":"","chapter":"49","title":"","lang_code":"gb","group_id":4419,"gro
up_name":"Tabunne Scans","group_id_2":0,"group_name_2":null,"group_id_3":0,"grou
p_name_3":null,"timestamp":1587054018},"875469":{"volume":"","chapter":"49","tit
le":"","lang_code":"fr","group_id":7367,"group_name":"Kawaii desu desu","group_i
d_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":158825
8192},"858693":{"volume":"","chapter":"48","title":"","lang_code":"gb","group_id
":4419,"group_name":"Tabunne Scans","group_id_2":0,"group_name_2":null,"group_id
_3":0,"group_name_3":null,"timestamp":1586888241},"874751":{"volume":"","chapter
":"48","title":"","lang_code":"fr","group_id":7367,"group_name":"Kawaii desu des
u","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timest
amp":1588166365},"855685":{"volume":"","chapter":"47","title":"","lang_code":"gb
","group_id":4419,"group_name":"Tabunne Scans","group_id_2":0,"group_name_2":nul
l,"group_id_3":0,"group_name_3":null,"timestamp":1586626602},"873893":{"volume":
"","chapter":"47","title":"","lang_code":"fr","group_id":7367,"group_name":"Kawa
ii desu desu","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":n
ull,"timestamp":1588083562},"853692":{"volume":"","chapter":"46","title":"","lan
g_code":"gb","group_id":4419,"group_name":"Tabunne Scans","group_id_2":0,"group_
name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1586446574},"873223"
:{"volume":"","chapter":"46","title":"","lang_code":"fr","group_id":7367,"group_
name":"Kawaii desu desu","group_id_2":0,"group_name_2":null,"group_id_3":0,"grou
p_name_3":null,"timestamp":1588027352},"852915":{"volume":"","chapter":"45","tit
le":"","lang_code":"gb","group_id":4419,"group_name":"Tabunne Scans","group_id_2
":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":158636150
9},"870093":{"volume":"","chapter":"45","title":"","lang_code":"fr","group_id":7
367,"group_name":"Kawaii desu desu","group_id_2":0,"group_name_2":null,"group_id
_3":0,"group_name_3":null,"timestamp":1587821395},"852914":{"volume":"","chapter
":"44","title":"","lang_code":"gb","group_id":4419,"group_name":"Tabunne Scans",
"group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp
":1586361458},"869202":{"volume":"","chapter":"44","title":"","lang_code":"fr","
group_id":7367,"group_name":"Kawaii desu desu","group_id_2":0,"group_name_2":nul
l,"group_id_3":0,"group_name_3":null,"timestamp":1587742218},"851137":{"volume":
"","chapter":"43","title":"","lang_code":"gb","group_id":4419,"group_name":"Tabu
nne Scans","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null
,"timestamp":1586191630},"867351":{"volume":"","chapter":"43","title":"","lang_c
ode":"fr","group_id":7367,"group_name":"Kawaii desu desu","group_id_2":0,"group_
name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1587645242},"848682"
:{"volume":"","chapter":"42","title":"","lang_code":"gb","group_id":4419,"group_
name":"Tabunne Scans","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_n
ame_3":null,"timestamp":1586014091},"866554":{"volume":"","chapter":"42","title"
:"","lang_code":"fr","group_id":7367,"group_name":"Kawaii desu desu","group_id_2
":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":158756861
3},"847769":{"volume":"","chapter":"41","title":"","lang_code":"gb","group_id":4
419,"group_name":"Tabunne Scans","group_id_2":0,"group_name_2":null,"group_id_3"
:0,"group_name_3":null,"timestamp":1585927490},"865672":{"volume":"","chapter":"
41","title":"","lang_code":"fr","group_id":7367,"group_name":"Kawaii desu desu",
"group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp
":1587470441},"846254":{"volume":"","chapter":"40","title":"","lang_code":"gb","
group_id":4419,"group_name":"Tabunne Scans","group_id_2":0,"group_name_2":null,"
group_id_3":0,"group_name_3":null,"timestamp":1585761265},"865285":{"volume":"",
"chapter":"40","title":"","lang_code":"fr","group_id":7367,"group_name":"Kawaii 
desu desu","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null
,"timestamp":1587422151},"844960":{"volume":"","chapter":"39","title":"","lang_c
ode":"gb","group_id":4419,"group_name":"Tabunne Scans","group_id_2":0,"group_nam
e_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1585661233},"852967":{"
volume":"","chapter":"39","title":"","lang_code":"fr","group_id":7367,"group_nam
e":"Kawaii desu desu","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_n
ame_3":null,"timestamp":1586366391},"844176":{"volume":"","chapter":"38","title"
:"","lang_code":"gb","group_id":4419,"group_name":"Tabunne Scans","group_id_2":0
,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1585596269},
"849885":{"volume":"","chapter":"38","title":"","lang_code":"fr","group_id":7367
,"group_name":"Kawaii desu desu","group_id_2":0,"group_name_2":null,"group_id_3"
:0,"group_name_3":null,"timestamp":1586100345},"842339":{"volume":"","chapter":"
37","title":"","lang_code":"gb","group_id":4419,"group_name":"Tabunne Scans","gr
oup_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1
585488492},"847545":{"volume":"","chapter":"37","title":"","lang_code":"fr","gro
up_id":7367,"group_name":"Kawaii desu desu","group_id_2":0,"group_name_2":null,"
group_id_3":0,"group_name_3":null,"timestamp":1585909302},"841884":{"volume":"",
"chapter":"36","title":"","lang_code":"gb","group_id":4419,"group_name":"Tabunne
 Scans","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"t
imestamp":1585423138},"847206":{"volume":"","chapter":"36","title":"","lang_code
":"fr","group_id":7367,"group_name":"Kawaii desu desu","group_id_2":0,"group_nam
e_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1585863365},"839130":{"
volume":"","chapter":"35","title":"","lang_code":"gb","group_id":4419,"group_nam
e":"Tabunne Scans","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name
_3":null,"timestamp":1585178716},"846349":{"volume":"","chapter":"35","title":""
,"lang_code":"fr","group_id":7367,"group_name":"Kawaii desu desu","group_id_2":0
,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1585775011},
"835863":{"volume":"","chapter":"34","title":"","lang_code":"gb","group_id":4419
,"group_name":"Tabunne Scans","group_id_2":0,"group_name_2":null,"group_id_3":0,
"group_name_3":null,"timestamp":1584793545},"836964":{"volume":"","chapter":"34"
,"title":"","lang_code":"fr","group_id":7367,"group_name":"Kawaii desu desu","gr
oup_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1
584909620},"833795":{"volume":"","chapter":"33","title":"","lang_code":"gb","gro
up_id":4419,"group_name":"Tabunne Scans","group_id_2":0,"group_name_2":null,"gro
up_id_3":0,"group_name_3":null,"timestamp":1584624078},"836318":{"volume":"","ch
apter":"33","title":"","lang_code":"fr","group_id":7367,"group_name":"Kawaii 
desu desu","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null
,"timestamp":1584836504},"827559":{"volume":"","chapter":"32","title":"","lang_c
ode":"gb","group_id":4419,"group_name":"Tabunne Scans","group_id_2":0,"group_nam
e_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1584104220},"834479":{"
volume":"","chapter":"32","title":"","lang_code":"fr","group_id":7367,"group_nam
e":"Kawaii desu desu","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_n
ame_3":null,"timestamp":1584655783},"826151":{"volume":"","chapter":"31","title"
:"","lang_code":"gb","group_id":4419,"group_name":"Tabunne Scans","group_id_2":0
,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1583958491},
"834478":{"volume":"","chapter":"31","title":"","lang_code":"fr","group_id":7367
,"group_name":"Kawaii desu desu","group_id_2":0,"group_name_2":null,"group_id_3"
:0,"group_name_3":null,"timestamp":1584655772},"823901":{"volume":"","chapter":"
30","title":"","lang_code":"gb","group_id":4419,"group_name":"Tabunne Scans","gr
oup_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1
583754780},"831399":{"volume":"","chapter":"30","title":"","lang_code":"fr","gro
up_id":7367,"group_name":"Kawaii desu desu","group_id_2":0,"group_name_2":null,"
group_id_3":0,"group_name_3":null,"timestamp":1584366792},"822858":{"volume":"",
"chapter":"29","title":"","lang_code":"gb","group_id":4419,"group_name":"Tabunne
 Scans","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"t
imestamp":1583637749},"825247":{"volume":"","chapter":"29","title":"","lang_code
":"fr","group_id":7367,"group_name":"Kawaii desu desu","group_id_2":0,"group_nam
e_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1583862645},"822146":{"
volume":"","chapter":"28","title":"","lang_code":"gb","group_id":4419,"group_nam
e":"Tabunne Scans","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name
_3":null,"timestamp":1583538308},"824475":{"volume":"","chapter":"28","title":""
,"lang_code":"fr","group_id":7367,"group_name":"Kawaii desu desu","group_id_2":0
,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1583786989},
"820228":{"volume":"","chapter":"27","title":"","lang_code":"gb","group_id":4419
,"group_name":"Tabunne Scans","group_id_2":0,"group_name_2":null,"group_id_3":0,
"group_name_3":null,"timestamp":1583334917},"823375":{"volume":"","chapter":"27"
,"title":"","lang_code":"fr","group_id":7367,"group_name":"Kawaii desu desu","gr
oup_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1
583695440},"819029":{"volume":"","chapter":"26","title":"","lang_code":"gb","gro
up_id":4419,"group_name":"Tabunne Scans","group_id_2":0,"group_name_2":null,"gro
up_id_3":0,"group_name_3":null,"timestamp":1583172467},"821182":{"volume":"","ch
apter":"26","title":"","lang_code":"fr","group_id":7367,"group_name":"Kawaii 
desu desu","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null
,"timestamp":1583442924},"817581":{"volume":"","chapter":"25","title":"","lang_c
ode":"gb","group_id":4419,"group_name":"Tabunne Scans","group_id_2":0,"group_nam
e_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1582997352},"820508":{"
volume":"","chapter":"25","title":"","lang_code":"fr","group_id":7367,"group_nam
e":"Kawaii desu desu","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_n
ame_3":null,"timestamp":1583358014},"816899":{"volume":"","chapter":"24","title"
:"","lang_code":"gb","group_id":4419,"group_name":"Tabunne Scans","group_id_2":0
,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1582906265},
"819054":{"volume":"","chapter":"24","title":"","lang_code":"fr","group_id":7367
,"group_name":"Kawaii desu desu","group_id_2":0,"group_name_2":null,"group_id_3"
:0,"group_name_3":null,"timestamp":1583175367},"815141":{"volume":"","chapter":"
23","title":"","lang_code":"gb","group_id":4419,"group_name":"Tabunne Scans","gr
oup_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1
582657649},"818411":{"volume":"","chapter":"23","title":"","lang_code":"fr","gro
up_id":7367,"group_name":"Kawaii desu desu","group_id_2":0,"group_name_2":null,"
group_id_3":0,"group_name_3":null,"timestamp":1583091890},"814370":{"volume":"",
"chapter":"22","title":"","lang_code":"gb","group_id":4419,"group_name":"Tabunne
 Scans","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"t
imestamp":1582566237},"818389":{"volume":"","chapter":"22","title":"","lang_code
":"fr","group_id":7367,"group_name":"Kawaii desu desu","group_id_2":0,"group_nam
e_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1583089261},"813627":{"
volume":"","chapter":"21","title":"","lang_code":"gb","group_id":4419,"group_nam
e":"Tabunne Scans","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name
_3":null,"timestamp":1582474888},"816965":{"volume":"","chapter":"21","title":""
,"lang_code":"fr","group_id":7367,"group_name":"Kawaii desu desu","group_id_2":0
,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1582915427},
"812941":{"volume":"","chapter":"20","title":"","lang_code":"gb","group_id":4419
,"group_name":"Tabunne Scans","group_id_2":0,"group_name_2":null,"group_id_3":0,
"group_name_3":null,"timestamp":1582401207},"816542":{"volume":"","chapter":"20"
,"title":"","lang_code":"fr","group_id":7367,"group_name":"Kawaii desu desu","gr
oup_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1
582841633},"812058":{"volume":"","chapter":"19","title":"","lang_code":"gb","gro
up_id":4419,"group_name":"Tabunne Scans","group_id_2":0,"group_name_2":null,"gro
up_id_3":0,"group_name_3":null,"timestamp":1582307867},"816541":{"volume":"","ch
apter":"19","title":"","lang_code":"fr","group_id":7367,"group_name":"Kawaii 
desu desu","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null
,"timestamp":1582841619},"810193":{"volume":"","chapter":"18","title":"","lang_c
ode":"gb","group_id":4419,"group_name":"Tabunne Scans","group_id_2":0,"group_nam
e_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1582134721},"812224":{"
volume":"","chapter":"18","title":"","lang_code":"fr","group_id":7367,"group_nam
e":"Kawaii desu desu","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_n
ame_3":null,"timestamp":1582578417},"809263":{"volume":"","chapter":"17","title"
:"","lang_code":"gb","group_id":4419,"group_name":"Tabunne Scans","group_id_2":0
,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1582049146},
"812223":{"volume":"","chapter":"17","title":"","lang_code":"fr","group_id":7367
,"group_name":"Kawaii desu desu","group_id_2":0,"group_name_2":null,"group_id_3"
:0,"group_name_3":null,"timestamp":1582491980},"808550":{"volume":"","chapter":"
16","title":"","lang_code":"gb","group_id":4419,"group_name":"Tabunne Scans","gr
oup_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1
581966564},"812219":{"volume":"","chapter":"16","title":"","lang_code":"fr","gro
up_id":7367,"group_name":"Kawaii desu desu","group_id_2":0,"group_name_2":null,"
group_id_3":0,"group_name_3":null,"timestamp":1582405447},"807770":{"volume":"",
"chapter":"15","title":"","lang_code":"gb","group_id":4419,"group_name":"Tabunne
 Scans","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"t
imestamp":1581877249},"812220":{"volume":"","chapter":"15","title":"","lang_code
":"fr","group_id":7367,"group_name":"Kawaii desu desu","group_id_2":0,"group_nam
e_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1582319117},"803798":{"
volume":"","chapter":"14","title":"","lang_code":"gb","group_id":4419,"group_nam
e":"Tabunne Scans","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name
_3":null,"timestamp":1581514272},"809237":{"volume":"","chapter":"14","title":""
,"lang_code":"fr","group_id":7367,"group_name":"Kawaii desu desu","group_id_2":0
,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1582216403},
"816494":{"volume":"","chapter":"13.5","title":"","lang_code":"gb","group_id":44
19,"group_name":"Tabunne Scans","group_id_2":0,"group_name_2":null,"group_id_3":
0,"group_name_3":null,"timestamp":1582836693},"821190":{"volume":"","chapter":"1
3.5","title":"Clarification","lang_code":"fr","group_id":7367,"group_name":"Kawa
ii desu desu","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":n
ull,"timestamp":1583443571},"802343":{"volume":"","chapter":"13","title":"","lan
g_code":"gb","group_id":4419,"group_name":"Tabunne Scans","group_id_2":0,"group_
name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1581352586},"804040"
:{"volume":"","chapter":"13","title":"","lang_code":"fr","group_id":7367,"group_
name":"Kawaii desu desu","group_id_2":0,"group_name_2":null,"group_id_3":0,"grou
p_name_3":null,"timestamp":1582148849},"800513":{"volume":"","chapter":"12","tit
le":"","lang_code":"gb","group_id":4419,"group_name":"Tabunne Scans","group_id_2
":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":158117877
4},"804039":{"volume":"","chapter":"12","title":"","lang_code":"fr","group_id":7
367,"group_name":"Kawaii desu desu","group_id_2":0,"group_name_2":null,"group_id
_3":0,"group_name_3":null,"timestamp":1582062389},"799720":{"volume":"","chapter
":"11","title":"","lang_code":"gb","group_id":4419,"group_name":"Tabunne Scans",
"group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp
":1581092522},"804038":{"volume":"","chapter":"11","title":"","lang_code":"fr","
group_id":7367,"group_name":"Kawaii desu desu","group_id_2":0,"group_name_2":nul
l,"group_id_3":0,"group_name_3":null,"timestamp":1581975946},"799199":{"volume":
"","chapter":"10","title":"","lang_code":"gb","group_id":4419,"group_name":"Tabu
nne Scans","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null
,"timestamp":1581005084},"804036":{"volume":"","chapter":"10","title":"","lang_c
ode":"fr","group_id":7367,"group_name":"Kawaii desu desu","group_id_2":0,"group_
name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1581889381},"798518"
:{"volume":"","chapter":"9","title":"","lang_code":"gb","group_id":4419,"group_n
ame":"Tabunne Scans","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_na
me_3":null,"timestamp":1580911239},"804035":{"volume":"","chapter":"9","title":"
","lang_code":"fr","group_id":7367,"group_name":"Kawaii desu desu","group_id_2":
0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1581802955}
,"797676":{"volume":"","chapter":"8","title":"","lang_code":"gb","group_id":4419
,"group_name":"Tabunne Scans","group_id_2":0,"group_name_2":null,"group_id_3":0,
"group_name_3":null,"timestamp":1580763401},"804032":{"volume":"","chapter":"8",
"title":"","lang_code":"fr","group_id":7367,"group_name":"Kawaii desu desu","gro
up_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":15
81716428},"797483":{"volume":"","chapter":"7","title":"","lang_code":"gb","group
_id":4419,"group_name":"Tabunne Scans","group_id_2":0,"group_name_2":null,"group
_id_3":0,"group_name_3":null,"timestamp":1580738905},"804017":{"volume":"","chap
ter":"7","title":"","lang_code":"fr","group_id":7367,"group_name":"Kawaii desu d
esu","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"time
stamp":1581629550},"794696":{"volume":"","chapter":"6","title":"","lang_code":"g
b","group_id":4419,"group_name":"Tabunne Scans","group_id_2":0,"group_name_2":nu
ll,"group_id_3":0,"group_name_3":null,"timestamp":1580521264},"803761":{"volume"
:"","chapter":"6","title":"","lang_code":"fr","group_id":7367,"group_name":"Kawa
ii desu desu","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":n
ull,"timestamp":1581509486},"793995":{"volume":"","chapter":"5","title":"","lang
_code":"gb","group_id":4419,"group_name":"Tabunne Scans","group_id_2":0,"group_n
ame_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1580480243},"803383":
{"volume":"","chapter":"5","title":"","lang_code":"fr","group_id":7367,"group_na
me":"Kawaii desu desu","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_
name_3":null,"timestamp":1581455701},"792548":{"volume":"","chapter":"4","title"
:"","lang_code":"gb","group_id":4419,"group_name":"Tabunne Scans","group_id_2":0
,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1580312581},
"802356":{"volume":"","chapter":"4","title":"","lang_code":"fr","group_id":7367,
"group_name":"Kawaii desu desu","group_id_2":0,"group_name_2":null,"group_id_3":
0,"group_name_3":null,"timestamp":1581354578},"792547":{"volume":"","chapter":"3
","title":"","lang_code":"gb","group_id":4419,"group_name":"Tabunne Scans","grou
p_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":158
0312552},"802357":{"volume":"","chapter":"3","title":"","lang_code":"fr","group_
id":7367,"group_name":"Kawaii desu desu","group_id_2":0,"group_name_2":null,"gro
up_id_3":0,"group_name_3":null,"timestamp":1581354664},"791355":{"volume":"","ch
apter":"2","title":"","lang_code":"gb","group_id":4419,"group_name":"Tabunne Sca
ns","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"times
tamp":1580139462},"802353":{"volume":"","chapter":"2","title":"","lang_code":"fr
","group_id":7367,"group_name":"Kawaii desu desu","group_id_2":0,"group_name_2":
null,"group_id_3":0,"group_name_3":null,"timestamp":1581354233},"791354":{"volum
e":"","chapter":"1","title":"","lang_code":"gb","group_id":4419,"group_name":"Ta
bunne Scans","group_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":nu
ll,"timestamp":1580139436},"793158":{"volume":"","chapter":"1","title":"","lang_
code":"fr","group_id":7367,"group_name":"Kawaii desu desu","group_id_2":0,"group
_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":1580401859},"816497
":{"volume":"","chapter":"0.1","title":"Character introduction extra 
pages","lang_code":"gb","group_id":4419,"group_name":"Tabunne Scans","group_id_2
":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":158283701
2},"819885":{"volume":"","chapter":"0.1","title":"Présentation des personnages 
bonus","lang_code":"fr","group_id":7367,"group_name":"Kawaii desu desu","group_i
d_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":158327
0399},"791356":{"volume":"","chapter":"0","title":"Character 
introduction","lang_code":"gb","group_id":4419,"group_name":"Tabunne Scans","gro
up_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":15
80139514},"792824":{"volume":"","chapter":"0","title":"Présentation des 
personnages","lang_code":"fr","group_id":7367,"group_name":"Kawaii desu desu","g
roup_id_2":0,"group_name_2":null,"group_id_3":0,"group_name_3":null,"timestamp":
1580336246}},"group":{"4419":{"group_name":"Tabunne 
Scans"},"7367":{"group_name":"Kawaii desu desu"}},"status":"OK"} 
""", 200)


# def oneshot_intermixed():

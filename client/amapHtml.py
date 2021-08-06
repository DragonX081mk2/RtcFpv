AmapHTML = '''
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no, width=device-width">
    <link rel="stylesheet" href="https://a.amap.com/jsapi_demos/static/demo-center/css/demo-center.css" />
    <title>地图显示</title>
    <style>
        html,
        body,
        #container {
          width: 100%;
          height: 100%;
        }
    </style>
</head>
<body>
<div id="container"></div>
<!-- 加载地图JSAPI脚本 -->
<script src="https://webapi.amap.com/loader.js"></script>
<script type="text/javascript" src="https://webapi.amap.com/maps?v=1.4.15&key=0fe4f8ec56db3d50f341eaeeb74675d7"></script> 
<script type="text/javascript" >
// AMapLoader.load({
//     "key": "0fe4f8ec56db3d50f341eaeeb74675d7",              // 申请好的Web端开发者Key，首次调用 load 时必填
//     "version": "1.4.15",   // 指定要加载的 JSAPI 的版本，缺省时默认为 1.4.15
//     "plugins": [],           // 需要使用的的插件列表，如比例尺'AMap.Scale'等
//     "AMapUI": {             // 是否加载 AMapUI，缺省不加载
//         "version": '1.1',   // AMapUI 缺省 1.1
//         "plugins":['overlay/SimpleMarker'],       // 需要加载的 AMapUI ui插件
//     },
//     "Loca":{                // 是否加载 Loca， 缺省不加载
//         "version": '1.3.2'  // Loca 版本，缺省 1.3.2
//     },
// }).then((AMap)=>{
//         var map = new AMap.Map('container');
//         map.addControl(new AMap.Scale());
//         new AMapUI.SimpleMarker({
//             map: map,
//             position: map.getCenter(),
//         });
//     }).catch((e)=>{
//         console.error(e);  //加载错误提示
//     });

var map = new AMap.Map('container');   
var layer = new AMap.TileLayer.Satellite();
map.add([layer]);
var loca_mark = new AMap.Marker({icon:'./img/ustc.png',offset:{x:-20,y:-15}});
map.add(loca_mark);

function setLocation(lat,lon) {
  loca_mark.setPosition(new AMap.LngLat(lat,lon));
}

function setAngle(angle) {
  loca_mark.setAngle(angle);
}
</script>
</body>
</html>
'''
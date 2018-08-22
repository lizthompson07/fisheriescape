function popitup(url,windowName,hgt=500,wdt=500,top=50,left=200) {
  console.log(strWindowFeatures);
  console.log(hgt);
  console.log(wdt);
    var strWindowFeatures = "height="+hgt+",width="+wdt+",top="+top+",left="+left;
    newwindow=window.open(url,windowName,strWindowFeatures);
    if (window.focus) {newwindow.focus()}
    return false;
}

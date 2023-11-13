console.log('dupl analytics lives on')

function sendData( data, url='https://analytics.marcusj.org/api/hit' ) {
    const XHR = new XMLHttpRequest(),
    FD  = new FormData();

    // Push our data into our FormData object
    for( name in data ) {
        FD.append( name, data[ name ] );
    }

    // Define what happens in case of error
    XHR.addEventListener(' error', function( event ) {
        console.log('analytics: post error');
    } );

    // Set up our request
    XHR.open( 'POST', url );

    // Send our FormData object; HTTP headers are set automatically
    XHR.send( FD );
}

function getJSON(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.responseType = 'json';
    xhr.onload = function() {
      var status = xhr.status;
      if (status === 200) {
        callback(null, xhr.response);
      } else {
        callback(status, xhr.response);
      }
    };
    xhr.send();
};

const getDeviceType = () => {
  const ua = navigator.userAgent;
  if (/(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(ua)) {
    return "tablet";
  }
  if (
    /Mobile|iP(hone|od|ad)|Android|BlackBerry|IEMobile|Kindle|Silk-Accelerated|(hpw|web)OS|Opera M(obi|ini)/.test(
      ua
    )
  ) {
    return "mobile";
  }
  return "desktop";
};

document.addEventListener('DOMContentLoaded', function() {
    getJSON("https://geolocation-db.com/json/", (s, r) => {
        sendData({
            "Domain": window.location.hostname,
            "Route": window.location.pathname,
            "Browser": (function (agent) {
                switch (true) {
                    case agent.indexOf("edge") > -1: return "edge";
                    case agent.indexOf("edg") > -1: return "chromium based edge (dev or canary)";
                    case agent.indexOf("opr") > -1 && !!window.opr: return "opera";
                    case agent.indexOf("chrome") > -1 && !!window.chrome: return "chrome";
                    case agent.indexOf("trident") > -1: return "ie";
                    case agent.indexOf("firefox") > -1: return "firefox";
                    case agent.indexOf("safari") > -1: return "safari";
                    default: return "other";
                }
            })(window.navigator.userAgent.toLowerCase()),
            "Location": r['country_name'],
            "Device": getDeviceType(),
            "Referrer": document.referrer.split('/')[2],
        })
    })
})

var show = document.currentScript.getAttribute('show');
if (show != null) {
    function showAnalytics() {
        getJSON("https://analytics.marcusj.org/getAllVisits/" + window.location.hostname, (s, r) => {
            var visits = r.visits[0].visits;
            var el = document.getElementById('analytics');
            el.innerHTML = `<div style='display: flex; width: fit-content; height: 50px; padding: 6px 4px; border-radius: 5px; background-color: #1d2333; color: #f3f3f3; align-items: center; font-weight: 600; cursor: pointer;' onclick='window.location = "https://analytics.marcusj.org/${window.location.hostname}";'><img style='width: auto; height: inherit;' src='https://analytics.marcusj.org/static/dupl-analytics-1.png' /> <div>dupl analytics<br><span style='font-size: 14px; color: rgba(200,200,200,0.7);'>${visits} VISITS</span></div></div>`;
        })
    }
}
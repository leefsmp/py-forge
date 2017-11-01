/////////////////////////////////////////////////////////
// Initialize viewer environment
//
/////////////////////////////////////////////////////////
function initialize (options) {

  return new Promise(function(resolve, reject) {

    Autodesk.Viewing.Initializer (options,
      function () {

        resolve ()

      }, function(error){

        reject (error)
      })
  })
}

/////////////////////////////////////////////////////////
// load document from URN
//
/////////////////////////////////////////////////////////
function loadDocument (urn) {

  return new Promise(function(resolve, reject) {

    var paramUrn = !urn.startsWith("urn:")
      ? "urn:" + urn
      : urn

    Autodesk.Viewing.Document.load(paramUrn,
      function(doc) {

        resolve (doc)

      }, function (error) {

        reject (error)
      })
  })
}

/////////////////////////////////////////////////////////
// Get viewable items from document
//
/////////////////////////////////////////////////////////
function getViewableItems (doc, roles) {

  var rootItem = doc.getRootItem()

  var items = []

  var roleArray = roles
    ? (Array.isArray(roles) ? roles : [roles])
    : []

  roleArray.forEach(function(role) {

    var subItems =
      Autodesk.Viewing.Document.getSubItemsWithProperties(
        rootItem, { type: "geometry", role: role }, true)

    items = items.concat(subItems)
  })

  return items
}

/////////////////////////////////////////////////////////
//
//
/////////////////////////////////////////////////////////
function getAccessToken(callback) {

  var xhttp = new XMLHttpRequest()

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {

      var res = JSON.parse(this.responseText)
      callback(res.access_token, res.expires_in)
    }
  }

  xhttp.open("GET", '/forge/token', true)
  xhttp.setRequestHeader("Content-type", "application/json")
  xhttp.send()
}

/////////////////////////////////////////////////////////
// Initialize Environment
//
/////////////////////////////////////////////////////////
function loadURN(urn) {

    initialize({

      getAccessToken: getAccessToken,
      env: "AutodeskProduction"

    }).then(function() {

      loadDocument (urn).then(function(doc) {

        var items = getViewableItems (doc, ["3d", "2d"])

        var path = doc.getViewablePath(items[0])

        var viewerDiv = document.getElementById("viewer")

        var viewer = new Autodesk.Viewing.Private.GuiViewer3D(viewerDiv)

        viewer.start(path)
      })
    })
}


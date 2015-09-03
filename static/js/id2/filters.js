
// Purloined from http://stackoverflow.com/questions/10420352/converting-file-size-in-bytes-to-human-readable
ID2.App.filter('filesize', function() {
    return function(fileSize) {
      var i = -1;
      var byteUnits = ['kB', 'MB', 'GB', ' TB', 'PB', 'EB', 'ZB', 'YB'];
      do {
          fileSize = fileSize / 1024;
          i++;
      } while (fileSize > 1024);
      return Math.max(fileSize, 0.1).toFixed(1) + ' ' + byteUnits[i];
    }
});

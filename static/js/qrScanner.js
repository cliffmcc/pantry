$(function() {
    let _scannerIsRunning = false;
    let _html5QrcodeScanner = null;

    const Scanner_App = {
        init: function() {
            _html5QrcodeScanner = new Html5Qrcode("reader");
        },
        runScan: function() {
            const config = { fps: 10, qrbox: 250 };
            // this._html5QrcodeScanner.render(this.scanSuccess, this.scanError);
            _html5QrcodeScanner.start({ facingMode: "environment" }, config, this.scanSuccess);
            _scannerIsRunning = true;
        },
        stopScanner: function() {
            if (_scannerIsRunning) {
                _html5QrcodeScanner.stop().then((ignore) => {
                    // QR Code scanning is stopped.
                    _scannerIsRunning = false;
                }).catch((err) => {
                    // Stop failed, handle it.
                });
            }
        },
        scanSuccess: function(decodedText, decodedResult) {
            if (decodedText.length == 13) {
                document.getElementById("upcInput").setAttribute('value', decodedText);
                $('#scanBox').effect( "shake" )
            }
        },
        scanError: function (error) {
            // handle scan failure, usually better to ignore and keep scanning.
            // for example:
            console.warn(`Code scan error = ${error}`);
        }
    };

    $("#scanButton").click(function(){
        if (_scannerIsRunning) {
            Scanner_App.stopScanner();
        }
        else {
            Scanner_App.init();
            Scanner_App.runScan();
        }
    });
});

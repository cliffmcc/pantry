$(function() {
    let _scannerIsRunning = false;

    const Scanner_App = {
        init: function() {
            Quagga.init({
                inputStream: {
                    name: "Live",
                    type: "LiveStream",
                    target: document.querySelector('#interactive'),
                    constraints: {
                        width: 640,
                        height: 420,
                        facingMode: "environment"
                    },
                },
                numOfWorkers: 4,
                decoder: {
                    readers: [
//                        "code_128_reader",
//                        "ean_reader",
//                        "ean_8_reader",
//                        "code_39_reader",
//                        "code_39_vin_reader",
//                        "codabar_reader",
                        "upc_reader",
                        "upc_e_reader"
//                        "i2of5_reader"
                    ],
                    debug: {
                        showCanvas: true,
                        showPatches: true,
                        showFoundPatches: true,
                        showSkeleton: true,
                        showLabels: true,
                        showPatchLabels: true,
                        showRemainingPatchLabels: true,
                        boxFromPatches: {
                            showTransformed: true,
                            showTransformedBox: true,
                            showBB: true
                        }
                    },
                    multiple: false
                },
            },
            function (err) {
                if (err) {
                    console.log(err);
                    return
                }

                console.log("Initialization finished. Ready to start");
                _scannerIsRunning = true;
                Quagga.start();
            });
        },
        runScan: function() {
            Quagga.onProcessed(function (result) {
                const drawingCtx = Quagga.canvas.ctx.overlay,
                drawingCanvas = Quagga.canvas.dom.overlay;

                if (result) {
                    if (result.boxes) {
                        drawingCtx.clearRect(0, 0, parseInt(drawingCanvas.getAttribute("width")), parseInt(drawingCanvas.getAttribute("height")));
                        result.boxes.filter(function (box) {
                            return box !== result.box;
                        }).forEach(function (box) {
                            Quagga.ImageDebug.drawPath(box, { x: 0, y: 1 }, drawingCtx, { color: "green", lineWidth: 2 });
                        });
                    }

                    if (result.box) {
                        Quagga.ImageDebug.drawPath(result.box, { x: 0, y: 1 }, drawingCtx, { color: "#00F", lineWidth: 2 });
                    }

                    if (result.codeResult && result.codeResult.code) {
                        Quagga.ImageDebug.drawPath(result.line, { x: 'x', y: 'y' }, drawingCtx, { color: 'red', lineWidth: 3 });
                    }
                }
            });

            Quagga.onDetected(function (result) {
                var upc_scanned = result.codeResult.code;
                console.log("Barcode detected and processed : [" + upc_scanned + "]", result);
                if (upc_scanned.length >= 12) {
                    document.getElementById("upcInput").setAttribute('value', upc_scanned);
                    Scanner_App.stop();
                }
            });
        },
        stop: function() {
            Quagga.stop();
            $("#interactive").hide(500)
            this._scannerIsRunning = false;
        }
    };

    $("#scanButton").click(function(){
        if (Scanner_App._scannerIsRunning) {
            Scanner_App.stop();
            $("#interactive").hide(500)
        }
        else {
            $("#interactive").show(500)
            Scanner_App.init();
            Scanner_App.runScan();
        }
    });
});

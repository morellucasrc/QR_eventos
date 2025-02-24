document.addEventListener("DOMContentLoaded", function () {
    const video = document.getElementById("video");
    const canvas = document.getElementById("canvas");
    const context = canvas.getContext("2d");
    const scannedInfo = document.getElementById("scanned-info");

    navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
        .then((stream) => {
            video.srcObject = stream;
        })
        .catch((err) => {
            console.error("Error accediendo a la cámara: ", err);
        });

    function scanQRCode() {
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        canvas.toBlob((blob) => {
            const formData = new FormData();
            formData.append("qr_image", blob);

            fetch("/scan", {
                method: "POST",
                body: formData,
            })
            .then(response => response.text())
            .then(data => {
                scannedInfo.textContent = "Asistencia registrada: " + data;
            })
            .catch(error => {
                console.error("Error al escanear el QR:", error);
            });
        }, "image/png");
    }

    setInterval(scanQRCode, 1000); // Escanea automáticamente cada 1 segundo
});
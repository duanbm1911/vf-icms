document.getElementById('preview-btn').addEventListener('click', function () {
    const htmlCode = document.getElementById('code-editor').value;
    const previewFrame = document.getElementById('preview-frame');
    previewFrame.srcdoc = htmlCode;
});
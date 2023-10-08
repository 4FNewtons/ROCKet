const fileInput = document.getElementById('fileInput');
const uploadButton = document.getElementById('uploadButton');
const imagePreview = document.getElementById('imagePreview');

fileInput.addEventListener('change', () => {
  const file = fileInput.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (event) => {
      const imageUrl = event.target.result;
      imagePreview.innerHTML = `<img src="${imageUrl}" alt="Предпросмотр картинки">`;
    };
    reader.readAsDataURL(file);
  }
});

uploadButton.addEventListener('click', () => {
  const file = fileInput.files[0];
  if (file) {
    const formData = new FormData();
    formData.append('image', file);

    fetch('/speech', {
      method: 'POST',
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        console.log('Картинка успешно отправлена на сервер:', data);
      })
      .catch((error) => {
        console.error('Произошла ошибка при отправке картинки:', error);
      });
  } else {
    console.error('Файл не выбран.');
  }
});

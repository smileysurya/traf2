document.addEventListener('DOMContentLoaded', function() {
    // Simple form validation
    const uploadForm = document.querySelector('form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            const fileInput = document.getElementById('video');
            if (fileInput.files.length === 0) {
                e.preventDefault();
                alert('Please select a video file to upload');
            } else {
                // Show loading state
                const submitBtn = e.target.querySelector('button[type="submit"]');
                submitBtn.innerHTML = 'Processing...';
                submitBtn.disabled = true;
            }
        });
    }
});
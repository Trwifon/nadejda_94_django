document.querySelectorAll('input, textarea, select').forEach(field => {
    field.addEventListener('keydown', handleEnter);
});
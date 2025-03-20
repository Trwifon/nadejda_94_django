document.querySelectorAll('input, textarea').forEach(field => {
    field.addEventListener('keydown', handleEnter);
});
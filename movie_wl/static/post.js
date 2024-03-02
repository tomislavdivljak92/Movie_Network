document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.getElementById('multiline-input');

    textarea.addEventListener('input', function() {
        const lines = this.value.split('\n');
        const lastLine = lines[lines.length - 1];
        const cursorPosition = this.selectionStart;

        if (lastLine.length === this.cols && cursorPosition === this.value.length) {
            this.value += '\n';
        }
    });
});
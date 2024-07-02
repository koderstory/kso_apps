export function initializeMyComponent(): void {
    const element = document.createElement('div');
    element.innerHTML = '<h3>This is a custom component</h3>';
    element.style.color = "red";
    document.body.appendChild(element);
}
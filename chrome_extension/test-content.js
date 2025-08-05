// Minimal test script
alert('TEST: Extension is loading!');
console.log('TEST: Extension loaded successfully');

// Add a visible element to the page
const testDiv = document.createElement('div');
testDiv.innerHTML = 'EXTENSION TEST - IF YOU SEE THIS, IT WORKS';
testDiv.style.cssText = `
    position: fixed;
    top: 10px;
    right: 10px;
    background: red;
    color: white;
    padding: 10px;
    z-index: 99999;
    font-size: 16px;
    border: 3px solid white;
`;
document.body.appendChild(testDiv);

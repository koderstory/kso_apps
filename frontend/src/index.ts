import './styles/main.scss';
import { showAlert } from './utils/helper';
import { initializeMyComponent } from './components/component1';

const message: string = 'Hello, TypeScript with Webpack and Babel!';
console.log(message);

showAlert(message);
initializeMyComponent();

import React from 'react';
import {createRoot} from 'react-dom/client';
import DemoPaymentPreview from './DemoPaymentPreview.jsx';
import './style.css';
import './workspace.css';

createRoot(document.getElementById('root')).render(
  <DemoPaymentPreview />
);

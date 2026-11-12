import React from 'react';
import {createRoot} from 'react-dom/client';
import {BrowserRouter,Routes,Route} from 'react-router';
import {bootstrap} from './api';
import {App} from './App';
bootstrap().then(client=>createRoot(document.getElementById('root')).render(<BrowserRouter><Routes><Route path="*" element={<App client={client}/>}/></Routes></BrowserRouter>)).catch(error=>createRoot(document.getElementById('root')).render(<main className="empty"><h1>PatiKitap</h1><p role="alert">{error.message}</p><button className="primary" onClick={()=>window.location.reload()}>Yeniden dene</button></main>));

import React from 'react';
import {createBrowserRouter, RouterProvider} from 'react-router-dom';
import Home from './Pages/Home';
import Layout from './Components/Layout';
import SaveApi from './Pages/SaveApi';

const router = createBrowserRouter([{
  path: '/',
  element: <Layout />,
  children: [
    {path: '', element: <Home />},
    {path: 'save-api', element: <SaveApi />}
  ]
}])

function App() {
  return (
    <RouterProvider router={router}/>
  )
}

export default App
import logo from './logo.svg';
import './App.css';
import Header from './component/header/Header';
import Banner from './component/banner/Banner';

import React,{ Suspense } from 'react';
import { BrowserRouter, Switch, Redirect, Route, Router } from 'react-router-dom';
import NotFound from './component/NotFound/NotFound.jsx';
function App() {
    const ProductRouter = React.lazy(()=>import('./component/router/router'));

    
  
  return (
    <div className="bg-black">

      <Suspense fallback={<div>Loading....</div>}>
            <BrowserRouter>
                    <Header ></Header>
                    <Banner></Banner>
                      <Switch>
                        <Redirect exact from="/" to="/products" ></Redirect>

                        <Route path="/products" component={ProductRouter}></Route>
                        
                        <Route conponent={NotFound}></Route>
                      </Switch>





            </BrowserRouter>



      </Suspense>


      
      
     
   
    </div>
  );
}

export default App;

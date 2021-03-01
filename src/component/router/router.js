import React from 'react';
import { Switch, Route, useRouteMatch } from 'react-router-dom';
import Product from '../product/Product';
import EditProduct from './../editProduct/editProduct';
import NotFound from '../NotFound/NotFound';

function Router(props) {
    const match = useRouteMatch();
    console.log('match',match);
    
    return (
       <Switch>
           <Route exact path={match.url} component={Product}></Route>

           <Route path={`${match.url}/add`} component={EditProduct}></Route>
           <Route path={`${match.url}/:productId`} component={EditProduct}></Route>


           <Route component={NotFound} />
       </Switch>
    );
}

export default Router;
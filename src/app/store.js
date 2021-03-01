
import {configureStore} from '@reduxjs/toolkit';
import productReducer from '../component/product/productSlice';

const rootReducer ={
    products:productReducer,
};


const store = configureStore({
    reducer:rootReducer,
});

export default store;
import { useSelector } from "react-redux";
import './Product.scss';
import {Link} from 'react-router-dom';
import { useState } from "react";


function Product ()
{
        const products = useSelector(state=>state.products);
        console.log();
        const initPagtion = products.filter((item,index)=> index<=(4*1)-1 && index>=(4*1)-4);
        const [showProd,setShowProd] = useState(initPagtion);

        console.log('showProd',showProd);

        const[checknumPagtion,setCheckNumPagtion]=useState();

        const totalPagtion =Math.trunc(products.length/3);

        const [checknumPag,setCheckNumPag] =useState(1);

        const numPagtion = [];

        for(let i =1;i<=totalPagtion;i++)
        {
                numPagtion.push(i);

        }

       // console.log( 'numPagtion',numPagtion);


       const changePagtion = (numItem)=>
       {
        setCheckNumPag(numItem);
           // console.log( 'item',numItem);
            
            const showitemPagtion = products.filter((item,index)=> index<=(4*numItem)-1 && index>=(4*numItem)-4);

            setShowProd(showitemPagtion);
         //   console.log(showProd);



       }


       
       const NextPag=(num)=>
       {
           if((num-1)===totalPagtion)
           {
            changePagtion(1);
           }
           else
                {changePagtion(num);}
        

       };

       
       const PrevPag=(num)=>
       {
           if((num+1)===1)
           {
            changePagtion(totalPagtion);
           }
           else
                {changePagtion(num);}
        

       }

        



       // setShowProd( products.filter((item,index)=>index<=5));
            
     
            
               
            

       
        
       
        

    return(
        <>
        <div className="productlist">
            {
                showProd.map((item,key) =>(

                    <div key={item.title} className="productlist__item">
                                <div  className="productlist__item__photo">

                                        <img src={item.photo}></img>
                                
                                </div>

                                <div className="productlist__item__button">
                                    <button >View Infomation</button>
                                </div>

                                <div className="productlist__item__title">
                                    <p>{item.title}</p>
                                </div>


                    </div>

                   

                   

                ))
            }

           

           
            

        </div >
       

        <div className="displayFlex">

        <button onClick={()=>PrevPag(checknumPag-1)}>Next</button>
             
           
            {
                numPagtion.map((item,index)=>(
                    <button className={index===checknumPag-1?'active':''} key ={index} onClick={()=>changePagtion(item)}>
                            {item}
                    </button>

                        ))
            }

           
             <button onClick={()=>NextPag(checknumPag+1)}>Next</button>

            
           
         </div>
         <div className="text-red"><button><Link to="/products/add">Edit Products</Link></button></div>
         </>
    );
}

export default Product;
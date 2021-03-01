import './Banner.scss';
import huou from './../../assets/images/Re1c15e32b0c48fe1a45dbb6d3df65cc7.jfif';
import nam from './../../assets/images/R36e8406ea030e3325509f0600acef527.jfif';
import dragon from './../../assets/images/dragons-background-20.png';
import { useState, useEffect,setInterval } from 'react';

function Banner()
{
    const image =[huou,nam,dragon];
    const [slide, setSlide] = useState(image[0]);





    
    function handlePrevSlide()
    {
           const index = image.findIndex(x=>x===slide);
           
           if(index<1)
           {
               setSlide(image[image.length-1]);

           }
           else
           {
            setSlide(image[index-1]);
           }

    }

    useEffect(()=>{

        const timeOutSlide = setTimeout(handleNextSlide, 3000);

        return ()=>{

            clearTimeout(timeOutSlide);
        }
    },[image]);
    

        
    function handleNextSlide()
    {
           const index = image.findIndex(x=>x===slide);
          
           if(index===image.length-1)
           {
               setSlide(image[0]);

           }
           else
           {
            setSlide(image[index+1]);
           }

    }

   
    return (
        <div  className="banner">
            <div className="banner__image">
                <img src={slide} />
            </div>
            

           
                <a className="banner__prev" onClick={handlePrevSlide}>&#10094;</a>
                <a className="banner__next" onClick={handleNextSlide}>&#10095;</a>

               
            
            
                    
           
           

            
                    
        

           
                    
            
           
           
        </div>
       
        
    );
}


export default Banner;
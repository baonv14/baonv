import React,{useState} from 'react';
import './editProduct.scss';
import { Formik,ErrorMessage } from 'formik';
import {Input,Container,Form,FormGroup,Label,Button,FormFeedback} from 'reactstrap';
import * as Yup from 'yup';
import { useDispatch,useSelector } from 'react-redux';
import { addPhoto } from '../product/productSlice';

function EditProduct(props) {

    const Selector = useSelector(state=>state.products);
    const dispatch = useDispatch();
    

    const [tieudetxt,setTieudetxt]=useState();

    const validationSchema=Yup.object().shape({
        title:Yup.string().required('đ được để trống mô'),

    });


/*const handleSubmit =(values,actions)=>{
    //setTieudetxt();
   alert(values);
              //      console.log('values',values);
              //      console.log('actions',actions);
}
*/


    return (
     <Formik

         // GIÁ TRỊ KHỞI TẠO
        initialValues={
            {

            'title':'',
            'photo':''
            }
        }
           

            // ONSUBMIT
            onSubmit={
                (values,actions)=>{

                    const action = addPhoto(values);
                    dispatch(action);
                }
            }

            >
            {
                props=>
                (
                    <Container>

                            <Form onSubmit={props.handleSubmit}>

                                <FormGroup>
                                    <Label>tiêu đề</Label>
                                    <Input type='email'
                                            
                                            onChange={props.handleChange}
                                            onBlur={props.handleBlur}
                                            value={props.values.name}
                                            name='title'
                                            />
                                </FormGroup>


                                <FormGroup>
                                    <Label>Linh ảnh</Label>
                                    <Input type='text'
                                            
                                            onChange={props.handleChange}
                                            onBlur={props.handleChange}
                                            value={props.values.name}
                                            name='photo'
                                            />
                                </FormGroup>

                                <Button type='submit' >Submit</Button>

                            </Form>
                    </Container>
                )

            }



     </Formik>
    );
}

export default EditProduct;
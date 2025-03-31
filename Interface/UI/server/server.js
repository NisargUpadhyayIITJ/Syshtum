import axios from 'axios';

const getData = async (data) => {
    try {
        const response = await axios.post('http://127.0.0.1:8002/pipeline', {...data});
        console.log(response);
        return response.data;
    } catch (error) {
        console.error(error);
        return null;
    }
}


const ValidateKey = async (data)=>{
    const response = await axios.post('http://127.0.0.1:8002/validate', {...data});
    console.log(response);  
    return response.data;
}
const SaveApiKey = async (data)=>{
    const response = await axios.post('http://127.0.0.1:8002/enter_api', {...data});
    console.log(response);  
    return response.data;
}

export {
    getData,
    SaveApiKey,
    ValidateKey
};
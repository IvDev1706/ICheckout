//obtener capa de modal
const modal_layer = document.getElementsByClassName("modal_layer").item(0);
let modal_box = null;

//function para cambiar el estado
function setOpenModal(id){
    //quitar la clase hidden
    modal_layer.classList.remove("hidden");
    //mostrar caja
    modal_box = document.getElementById(id);
    modal_box.classList.remove("hidden");
}

//funcion para ocultar modal
function setCloseModal(id){
    //añadir la clase hidden
    modal_layer.classList.add("hidden");
    //ocultar caja
    modal_box = document.getElementById(id);
    modal_box.classList.add("hidden");
}
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import streamlit as st
import os
import base64
import time

# 设置页面配置
st.set_page_config(
    page_title="Nano人物背景转换平台",
    layout="wide"
)


SCENE_TEMPLATES = {
    "咖啡馆": "将以下人物放置在咖啡馆中，生成一张图片",
    "办公室": "将以下人物放置在现代化办公室中，生成一张图片",
    "海滩": "将以下人物放置在海滩上，生成一张图片",
    "公园": "将以下人物放置在美丽的公园中，生成一张图片",
    "图书馆": "将以下人物放置在安静的图书馆中，生成一张图片",
    "餐厅": "将以下人物放置在优雅的餐厅中，生成一张图片",
    "健身房": "将以下人物放置在健身房中，生成一张图片",
    "购物中心": "将以下人物放置在购物中心中，生成一张图片",
    "学校": "将以下人物放置在学校教室中，生成一张图片",
    "医院": "将以下人物放置在医院中，生成一张图片",
    "机场": "将以下人物放置在机场候机厅中，生成一张图片",
    "酒店": "将以下人物放置在豪华酒店中，生成一张图片"
}

def generate_images(prompt_template, uploaded_image, user_prompt='', num_images=4):
    """
    生成多张图片

    输入：提示词模版，用户提示词，上传的图片，生成图片数量
    输出：生成的图片列表
    
    """
    try:
        # 处理用户提示词为空的情况
        if user_prompt.strip():
            combined_prompt = f"{prompt_template}。{user_prompt}"
        else:
            combined_prompt = prompt_template
        
        client = genai.Client(api_key='AIzaSyCS9ThEjJDL05NlKwDyJqgYPUe9B0gCUlQ')
        generated_images = []
        
        for i in range(num_images):
            response = client.models.generate_content(
                model="gemini-2.5-flash-image-preview",
                contents=[combined_prompt, uploaded_image],
            )
            
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    image = Image.open(BytesIO(part.inline_data.data))
                    generated_images.append(image)
                    break
        
        return generated_images
        
    except Exception as e:
        st.error(f"生成图片时出错: {str(e)}")
        return []

def main():
    st.title("AI图像生成器")
    st.markdown("---")
    
    # 初始化session state
    if 'generated_images' not in st.session_state:
        st.session_state.generated_images = []
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False
    
    with st.sidebar:
        st.header("控制面板")
        
        # 场景选择
   
        selected_scene = st.selectbox(
            "选择场景模板",
            options=list(SCENE_TEMPLATES.keys()),
            index=0,
        )
        
    
        template_prompt = SCENE_TEMPLATES[selected_scene]
        
        st.markdown("---")

        uploaded_file = st.file_uploader(
            "选择图片文件",
            type=['png', 'jpg', 'jpeg'],
            help="支持PNG、JPG、JPEG格式"
        )
        
        st.markdown("---")
        
        user_prompt = st.text_area(
            "你的提示词（可选）",
            height=150,
            placeholder="例如：让这个人坐在窗边，手里拿着咖啡杯，阳光透过窗户洒在桌子上\n\n💡 提示：如果不输入任何内容，将只使用场景模板生成图片",
            help="描述你希望如何修改或增强图片。留空则只使用场景模板。"
        )
        
        st.markdown("---")
        
        num_images = st.slider("生成图片数量", 1, 10, 4)
    
   
    st.subheader("图片预览:")
    
    generate_button = False
    
    if uploaded_file is not None:
        st.subheader("当前上传的图片")
        uploaded_image = Image.open(uploaded_file)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(uploaded_image, caption="准备处理的图片", width=200)
        with col2:
            
            st.write(f"**文件名:** {uploaded_file.name}")
            st.write(f"**尺寸:** {uploaded_image.size[0]} × {uploaded_image.size[1]} 像素")
            st.write(f"**格式:** {uploaded_file.type.split('/')[-1].upper()}")
            st.write(f"**大小:** {uploaded_file.size / 1024:.1f} KB")
        

        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            generate_button = st.button(
                "生成图片",
                type="primary",
                use_container_width=True,
                disabled=uploaded_file is None
            )
    else:
        st.info("请在左侧上传一张图片开始使用")
    
    st.markdown("---")
    

    if generate_button and uploaded_file is not None:
        st.subheader("生成进度")
        st.info("开始生成图片...")
        
        with st.spinner("AI正在生成图片，请稍候..."):
            generated_images = generate_images(
                template_prompt, 
                uploaded_image, 
                user_prompt, 
                num_images
            )
            

            st.session_state.generated_images = generated_images
            st.session_state.show_results = True
    
 
    if st.session_state.show_results and st.session_state.generated_images:
        generated_images = st.session_state.generated_images
        st.markdown("---")
        st.subheader("生成结果")
        st.success(f"成功生成 {len(generated_images)} 张图片！")
        
        if len(generated_images) == 1:
            cols = st.columns(1)
        elif len(generated_images) == 2:
            cols = st.columns(2)
        elif len(generated_images) == 3:
            cols = st.columns(3)
        else:
            cols = st.columns(2)
        
        for i, img in enumerate(generated_images):
            with cols[i % len(cols)]:
                st.image(img, caption=f"生成图片 {i+1}", width=300)
                
                buf = BytesIO()
                img.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.download_button(
                    label=f"下载图片 {i+1}",
                    data=byte_im,
                    file_name=f"generated_image_{i+1}.png",
                    mime="image/png",
                    use_container_width=True
                )
        
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("清除结果", use_container_width=True):
                st.session_state.generated_images = []
                st.session_state.show_results = False
                st.rerun()

if __name__ == "__main__":
    main()
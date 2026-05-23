#escolher diret?rio manualmente
#para instalar pacotes, usar: install.packages("INSERIR NOME DO PACOTE")

#importar base de dados 
library(readr)
dados <- read_csv("AvaliaoClinicaDoEfei-Michelle_DATA_2025-02-28_0147.csv", 
                                                               col_types = cols(esq_q1_sem0 = col_number(), 
                                                                                esq_q2_sem0 = col_number(), esq_q3_sem0 = col_number(), 
                                                                                esq_q4_sem0 = col_number(), esq_q5_sem0 = col_number(), 
                                                                                esq_q6_sem0 = col_number(), esq_q7_sem0 = col_number(), 
                                                                                esq_q8_sem0 = col_number(), esq_q9_sem0 = col_number(), 
                                                                                esq_q10_sem0 = col_number(), esq_q11_sem0 = col_number(), 
                                                                                esq_q12_sem0 = col_number(), esq_q13_sem0 = col_number(), 
                                                                                esq_q14_sem0 = col_number(), esq_q15_sem0 = col_number(), 
                                                                                esq_q16_sem0 = col_number(), esq_q17_sem0 = col_number(), 
                                                                                esq_q18_sem0 = col_number(), esq_q19_sem0 = col_number(), 
                                                                                esq_q20_sem0 = col_number(), esq_q21_sem0 = col_number(), 
                                                                                esq_q22_sem0 = col_number(), esq_q23_sem0 = col_number(), 
                                                                                esq_q24_sem0 = col_number(), esq_q25_sem0 = col_number()))
View(dados)

#conhecer variáveis
library(dplyr)
glimpse(dados)

#excluir indivíduos com NA para todos os itens da ESQUADA
table(dados$esq_q1_sem0, useNA = "always")
dados1 <- dados[!is.na(dados$esq_q1_sem0),] #n=129
table(dados1$esq_q1_sem0, useNA = "always")

glimpse(dados1)

#criar base de dados apenas com itens ESQUADA e ID
#exclui dat_sem0
dados1 <- dados1[,-2]
#exclui rghc_sem0
dados1 <- dados1[,-2]
#exclui peso_sem0
dados1 <- dados1[,-2]
#exclui alt_sem0
dados1 <- dados1[,-2]
#exclui obs_sem0
dados1 <- dados1[,-27]

#calcular os escores
library(data.table)
library(mirt)
library(mirtCAT)

pars <- fread(input = "parTRUE_R.csv", header = T)
pars<- data.frame(a1=pars$a1,d1=pars$d1,d2=pars$d2,d3=pars$d3)
modelo<-generate.mirt_object(parameters = pars, itemtype = "graded")
escore<-fscores(object = modelo,method = "EAP",response.pattern = dados1[,-1], quadpts = 20, theta_lim = c(-4,4))
escore
escore<-data.frame(escore)

#classificação da qualidade da dieta - escala (0,1)
dados2 <- mutate(escore, escore.cat= case_when(F1 <=-2 ~ "muito ruim",
                                               F1 >-2.0 & F1 <=-1.0 ~ "ruim",
                                               F1 >-1.0 & F1 <= 0.5 ~ "boa",
                                               F1 > 0.5 & F1 <= 2.5 ~ "muito boa",
                                               F1 > 2.5 ~ "excelente"))

table(dados2$escore.cat, useNA = "always")

#TRANSFORMAÇÃO PARA A ESCALA(250,50)
dados2 <- mutate(dados2, F1novo=(dados2$F1*50)+250)
dados2 <- mutate(dados2, escore.cat.novo= case_when(F1novo <=150 ~ "muito ruim",
                                                    F1novo >150 & F1novo <=200 ~ "ruim",
                                                    F1novo >200 & F1novo <= 275 ~ "boa",
                                                    F1novo > 275 & F1novo <= 375 ~ "muito boa",
                                                    F1novo > 375 ~ "excelente"))
table(dados2$escore.cat.novo, useNA = "always")

#JUNTAR BANCO COM RESPOSTAS (dados) E BANCO COM ESCORES (dados2). BANCOS TÊM QUE TER VARIÁVEL COMUM
dados1 <- mutate(dados1, ID=1:129) 
dados2 <- mutate(dados2, ID=1:129)
dados3<-full_join(dados1,dados2)

#salvar arquivo com escores categorizados
write.csv2(dados3, file = paste0("qualidade-da-dieta.csv"))

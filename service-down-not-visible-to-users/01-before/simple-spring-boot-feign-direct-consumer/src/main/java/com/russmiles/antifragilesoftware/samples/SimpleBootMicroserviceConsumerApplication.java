package com.russmiles.antifragilesoftware.samples;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.netflix.feign.EnableFeignClients;
import org.springframework.cloud.netflix.feign.FeignClient;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import static org.springframework.web.bind.annotation.RequestMethod.GET;

@SpringBootApplication
@RestController
@EnableFeignClients
public class SimpleBootMicroserviceConsumerApplication {

    @FeignClient(name = "${consumed.microservice.name}", url = "${consumed.microservice.url}")
    interface HelloClient {
        @RequestMapping(value = "/", method = GET)
        String hello();
    }

    @Autowired
    private HelloClient client;

    @RequestMapping("/")
    public String home() {
        return "Simple Boot Microservice Consumer Alive!";
    }

    @RequestMapping("/invokeConsumedService")
    public String invokeConsumedService() {
        return client.hello();
    }

    public static void main(String[] args) {
        SpringApplication.run(SimpleBootMicroserviceConsumerApplication.class, args);
    }
}

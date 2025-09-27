'use client'

import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'
import { ChevronDown, Github, Linkedin, Mail, Download, Sparkles, Code2, Palette, Cpu } from 'lucide-react'

const Hero = () => {
  // Removed annoying word flipping - keeping it simple and professional

  const scrollToAbout = () => {
    const element = document.querySelector('#about')
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <section id="home" className="min-h-screen flex items-center relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 z-0">
        {/* Gradient Orbs */}
        <motion.div
          animate={{
            x: [0, 100, 0],
            y: [0, -50, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "linear"
          }}
          className="absolute top-20 left-20 w-72 h-72 bg-blue-500/20 rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            x: [0, -100, 0],
            y: [0, 50, 0],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: "linear"
          }}
          className="absolute bottom-20 right-20 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            x: [0, 50, 0],
            y: [0, -100, 0],
          }}
          transition={{
            duration: 30,
            repeat: Infinity,
            ease: "linear"
          }}
          className="absolute top-1/2 left-1/2 w-64 h-64 bg-green-500/20 rounded-full blur-3xl"
        />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 w-full">
        <div className="min-h-screen flex flex-col justify-center">
          {/* Main Heading - Left Aligned Like Madhav */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="mb-8 max-w-4xl"
          >
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight text-left">
              <span className="text-white">Anshika Tripathi</span>
              <br />
              <span className="text-gray-300">Full-Stack Developer</span>
              <br />
            </h1>
          </motion.div>

          {/* Subtitle - Left Aligned */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.5 }}
            className="mb-12 max-w-3xl"
          >
            <p className="text-xl md:text-2xl text-gray-300 leading-relaxed text-left">
              Your one-stop shop for modern web applications,<br />
              with more creativity and clean code.
            </p>
          </motion.div>

          {/* Contact Info - Left Aligned */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.7 }}
            className="space-y-6 max-w-2xl"
          >
            <p className="text-lg text-gray-400 text-left">
              Prefer Email and GitHub<br />
              if you need a quick response!
            </p>
          </motion.div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 2 }}
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
      >
        <motion.button
          onClick={scrollToAbout}
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="text-gray-400 hover:text-white transition-colors"
        >
          <ChevronDown className="w-6 h-6" />
        </motion.button>
      </motion.div>
    </section>
  )
}

export default Hero